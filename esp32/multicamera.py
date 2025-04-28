from machine import Pin, SPI, reset, UART
from camera import *
import os
fm = FileManager()

class MultiCamera:
    def __init__(self, spi, cs_pins, resolution, uart):
        self.ALL = '1' * len(cs_pins)
        self.uart = uart
        self.cams = {}
        
        for i, pin in enumerate(cs_pins):
            try: 
                cam = Camera(spi, pin, resolution)
                self.cams[i] = cam
                print(f"[MULTI]: Camera {i} initialized")
            except Exception as e:
                print(f"[MULTI] Failed to init camera {i}: {e}")
    
    def _mask_to_indices(self, mask):
        return [i for i, bit in enumerate(mask) if bit == '1']
    
    def _free_up_cameras(self):
        for cam in self.cams.values():
            cam.cs.on()
        sleep_ms(50)
        
    def send_over_uart(self, file_name):
        try:
            print("Attempting file transfer over UART...")
            with open(file_name, 'rb') as f:
                while True:
                    chunk = f.read(512)
                    if not chunk:
                        break
                    self.uart.write(chunk)
            
            self.uart.write(b'EOF')
            print("File transferred!")
        except Exception as e:
            print("Error sending file: ", e)

    def capture(self, enable_mask):
        # Capture on each camera
        selected_cams = self._mask_to_indices(enable_mask)
        file_names = []
            
        # Save and send over for each image captured
        for i in selected_cams:
            current_cam = self.cams[i]
            self._free_up_cameras()
            current_cam.capture_jpg()
            sleep_ms(50)
            
            file_name = f"{i}.jpg"
            print(f"[ESP]: Saving image from cam {i} to {file_name}")
            current_cam.save_jpg(file_name)
            file_names.append(file_name)
            self.send_over_uart(file_name)
            os.remove(file_name)
        
        capture_status = "Captured " + ", ".join(file_names) + "\n"
        self.uart.write(capture_status.encode())

    def set_resolution(self, resolution, enable_mask):
        cam_indices = self._mask_to_indices(enable_mask)
        for i in cam_indices:
            self.cams[i].resolution = resolution
        return f"[ESP]: Set resolution {resolution} on cams: {cam_indices}"
