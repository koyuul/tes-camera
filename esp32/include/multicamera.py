from include.camera import *
import os
fm = FileManager()

class MultiCamera:
    def __init__(self, spi, cs_pins, resolution, conn):
        self.ALL = '1' * len(cs_pins)
        self.conn = conn
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
        
    def send_image(self, file_name):
        try:
            print("Attempting file transfer...")
            with open(file_name, 'rb') as f:
                if self.conn.mode == "wifi":
                    chunk_size = 8192 # larger chunk size for WiFi
                else:
                    chunk_size = 512  # smaller chunk size for UART
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    self.conn.sendHost(chunk)  # sendHost will use WiFi or UART
            self.conn.sendHost(b'EOF')
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
            current_cam.save_jpg(file_name)
            file_names.append(file_name)
            self.send_image(file_name)
            os.remove(file_name)
            sleep_ms(1000)
            print(f"[ESP]: Saving image from cam {i} to {file_name}")
        
        #capture_status = "Captured " + ", ".join(file_names) + "\n"
        #self.conn.sendHost(capture_status)        

    def set_resolution(self, resolution, enable_mask):
        cam_indices = self._mask_to_indices(enable_mask)
        for i in cam_indices:
            self.cams[i].resolution = resolution
        return f"[ESP]: Set resolution {resolution} on cams: {cam_indices}"

    def health_check(self, enable_mask):
        """
        Ping each camera indicated by enable_mask (bitstring like '101').
        Returns dict {index: True/False} and sends a status string to host
        """
        results = {}
        selected = self._mask_to_indices(enable_mask)
        for i in selected:
            cam = self.cams.get(i)
            if cam is None:
                results[i] = False
                continue
            try:
                # Prefer explicit ping/test API if available
                if hasattr(cam, "ping"):
                    ok = bool(cam.ping())
                elif hasattr(cam, "test"):
                    ok = bool(cam.test())
                elif hasattr(cam, "check"):
                    ok = bool(cam.check())
                else:
                    # Fallback: perform a quick capture to verify camera responds
                    self._free_up_cameras()
                    cam.capture_jpg()
                    sleep_ms(50)
                    ok = True
                results[i] = bool(ok)
            except Exception as e:
                print(f"[MULTI] Health check cam {i} failed: {e}")
                results[i] = False
            sleep_ms(50)

        status_parts = [f"cam{idx}={'OK' if ok else 'FAIL'}" for idx, ok in sorted(results.items())]
        status = "[ESP]: HEALTH_CHECK: " + ", ".join(status_parts)
        try:
            self.conn.sendHost(status)
        except Exception as e:
            print(f"[MULTI] Failed to send health status: {e}")
        return results