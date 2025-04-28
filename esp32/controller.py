"""
NEXT STEPS:
- save resolutions
- save deactivated cams
"""
from machine import Pin, SPI, reset, UART
from camera import *
from multicamera import *
import time

# Connect to host device (over UART)
uart = UART(2, baudrate=115200, tx=26, rx=25)

def uart_readline(uart, end=b'\n'):
    buffer = b''
    while True:
        if uart.any():
            byte = uart.read(1)
            if byte:
                buffer += byte
                if byte == end:
                    return buffer

# Connect to LED
onboard_LED = Pin(2,  Pin.OUT)

def process(cmd):
    global cams
    cmd = cmd.decode().strip()
    print(f"[ESP]: Received: {cmd}")
    
    connected = False

    if ':' in cmd:
        command, arg_str = cmd.split(':', 1)
        args = arg_str.split(',') if arg_str else []
    else:
        command = cmd
        args = []

    if command == "CONNECT": # Exists separately to prevent hanging if one or more cameras can't connect
        enable_mask = args[0]
        resolution = args[1]
        if resolution not in Camera.valid_3mp_resolutions:
            uart.write(b"[ESP]: CONNECT failed. Resolution not valid for cameras.\n")
            return
        spi = SPI(2, baudrate=8000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
        cs_pins = [Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(4, Pin.OUT)]
        cams = MultiCamera(spi, cs_pins, resolution, uart)
        uart.write(b"[ESP]: Cameras connected successfully!\n")

    elif command == "CAPTURE":
        enable_mask = args[0]
        file_names = cams.capture(enable_mask)
        print("[ESP]: Capture and send complete!")
        
    elif command == "SET_RES":
        resolution = args[0]
        enable_mask = args[1] if len(args) > 1 else cams.ALL
        cams.set_resolution(resolution, enable_mask)
        set_res_status = f"Set resolution to {resolution} for cameras {enable_mask}\n"
        uart.write(set_res_status.encode())
        
    elif command == "HEALTH_CHK":
        enable_mask = args[0] if len(args) > 0 else cams.ALL
        cams.health_check(enable_mask)
    
    elif command == "PING":
        uart.write(b"PONG\n")
    
    else:
        uart.write(b"ERR: Command not found.\n")
        
print("[ESP]: Awaiting command...")

while True:
    if uart.any():
        line = uart_readline(uart)
        if line:
            process(line)
