import serial
from include.esp32_controller import ESP32Controller
from include.database_handler import DatabaseHandler

# Confirm ESP32 connection. Send a handshake to wait for connection before continuing.
print("[HOST]: Connecting to ESP32...")
esp32_uart_connection = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
esp32 = ESP32Controller(esp32_uart_connection)
passed = esp32.send_handshake()
if (passed):
    print("[HOST]: Handshake passed!")
else:
    print("[HOST]: Handshake timed out.")

# Request ESP32 connect to cameras. Kept separate in case a camera stops responding and needs to be disabled.
print("[HOST]: Connecting ESP32 to cameras...")
esp32.send_command("CONNECT:111,320x240")
esp32.read_response()

# Connect to database
print("[HOST]: Connecting to database...")
metadata_db = DatabaseHandler("/home/imager/tes-camera/image_info.db")
print("[HOST]: Database connected successfully!")

# Input loop
print("[HOST]: Entering input loop...")
while (True):
    # Take in input
    command = input("Enter command: ")
    
    # Break down arguments, if any
    args = []
    if ':' in command:
        operation, arg_str = command.split(':', 1)
        args = arg_str.split(',') if arg_str else []

    print(f"[HOST]: Sending command: {command}")
    esp32.send_command(command)
    
    # When sending a capture command, we expect to receive images back, so we organize and save them
    if command.startswith("CAPTURE"):
        print("[HOST]: Receiving image...")
        enable_mask = args[0]
        timeout_seconds = args[1] if len(args) > 1 else 10
        metadata_db.save_images(esp32_uart_connection, enable_mask, timeout_seconds)
        print("[HOST]: Image received and saved!")
    else:
        # Read back any responses
        print("[HOST]: Reading response...")
        resp = esp32.read_response()
        print(f"[HOST]: Received: {resp.decode()}")
