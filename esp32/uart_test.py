import serial
import time

# Adjust if your Pi uses ttyS0 instead of ttyAMA0
ser = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)

while True:
    # Send a test message
    ser.write(b"hello from pi\n")
    time.sleep(1)

    # Check if ESP sent anything back
    if ser.in_waiting > 0:
        data = ser.readline()
        print("Received:", data.decode(errors="ignore").strip())
