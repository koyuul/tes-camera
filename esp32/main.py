"""
NEXT STEPS:
- save resolutions
- save deactivated cams
"""
from machine import Pin, SPI, reset, UART
from include.camera import *
from include.multicamera import *
from include.connectionManager import ConnectionManager
import time
import sys

# --- Connect to ESP32 via WiFi or UART ---
conn = ConnectionManager()
print("[conn]: Initialized")
# Try WiFi first
try:
    wifi_connected = conn.initHostWifi()
    if wifi_connected == 200:
        print("[conn]: WiFi OK — using WiFi")
        conn.mode = "wifi"
    else:
        print("[conn]: WiFi not ok:", wifi_connected)
        conn.mode = None
except Exception as e:
    print("[conn]: WiFi error:", e)
    conn.mode = None
# Fall back to UART if WiFi failed
if not conn.mode:
    try:
        uart_connected = conn.initHostUART()
        if uart_connected == 200:
            print("[conn]: UART OK — using UART")
            conn.mode = "uart"
        else:
            print("[conn]: UART not ok:", uart_connected)
    except Exception as e:
        print("[conn]: UART error:", e)
# Check final result
if not conn.mode:
    print("[conn]: Both WiFi and UART failed. Exiting.")
    sys.exit(0)


def process(cmd):
    global cams
    cmd = cmd.strip()
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
        resolution = args[1] if len(args) > 1 else '1280x720'
        if resolution not in Camera.valid_3mp_resolutions:
            conn.sendHost("[ESP]: CONNECT failed. Resolution not valid for cameras.")
            return
        spi = SPI(2, baudrate=8000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
        cs_pins = [Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(4, Pin.OUT)]
        cams = MultiCamera(spi, cs_pins, resolution, conn)
        conn.sendHost("[ESP]: Cameras connected successfully!")

    elif command == "CAPTURE":
        enable_mask = args[0]
        file_names = cams.capture(enable_mask)
        print("[ESP]: Capture and send complete!")
        
    elif command == "SET_RES": # TODO: make this save in config
        resolution = args[0]
        enable_mask = args[1] if len(args) > 1 else cams.ALL
        cams.set_resolution(resolution, enable_mask)
        set_res_status = f"Set resolution to {resolution} for cameras {enable_mask}\n"
        conn.sendHost(set_res_status)
        
    elif command == "HEALTH_CHK": # TODO: finish this
        enable_mask = args[0] if len(args) > 0 else cams.ALL
        cams.health_check(enable_mask)
    
    elif command == "PING":
        conn.sendHost("PONG")
    
    else:
        conn.sendHost("ERR: Command not found.")
        
print("[main]: Awaiting command...")

while True:
    msg = conn.listenHost()
    if msg:
        print(f"[main]: got command: {msg}")
        process(msg)

