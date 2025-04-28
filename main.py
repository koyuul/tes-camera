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


# import socket
# import time
# from include.database_handler import DatabaseHandler
# from include.camera_controller import CameraController
# from include.recognition import RecognitionController
# from include.horizon_tracker import HorizonTrackerController

# # Connect to server and send a success signal
# print ("[CLI]: Connecting to server socket...")
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# try:
#     client_socket.connect(("127.0.0.1", 8080))
# except socket.error as e:
#     print(f"Failed to connect: {e}")
# client_socket.send("CONNECTION_SUCCESS".encode())

# # Connect to database
# print("[CLI]: Connecting to database...")
# metadata_db = DatabaseHandler()

# # Initiate camera
# print("[CLI]: Initiating cameras...")
# camera_controller = CameraController()

# # Initiate analysis packages
# recognition_controller = RecognitionController()
# horizon_tracker_controller = HorizonTrackerController()

# # Read packet data
# received_data = client_socket.recv(1024).decode()

# # Parse data for a command string
# print(f"[CLI]: Parsing {received_data}...")
# parsed = received_data.split("|")
# command = parsed[0]

# # 
# match command:
#     case "STD_CAPTURE":
#         camera_select = parsed[1]
#         request_epoch = parsed[2]
#         resolution = parsed[3] if parsed[3] is not None else None
#         camera_controller.capture(camera_select, request_epoch, resolution)
#     case "RETRIEVE":
#         arguments = parsed[1:]
#         database_handler.retrieve(arguments)
#     case "RECOGNIZE":
#         image_id = parsed[1] # you're welcome to change this if you want to implement it differently
#         # argument2 = ...
#         recognition_controller.recognize(image_id)
#     case "HORIZON":
#         image_id = parsed[1] # you're welcome to change this if you want to implement it differently
#         # argument2 = ...
#         horizon_tracker_controller.detect(image_id)
#     case _:
#         print(f"[CLI] Unrecognized command: {command}")