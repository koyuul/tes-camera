import socket
import time
from include.database_handler import DatabaseHandler
from include.camera_controller import CameraController
from include.recognition import RecognitionController
from include.horizon_tracker import HorizonTrackerController

# Connect to server and send a success signal
print ("[CLI]: Connecting to server socket...")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect(("127.0.0.1", 8080))
except socket.error as e:
    print(f"Failed to connect: {e}")
client_socket.send("CONNECTION_SUCCESS".encode())

# Connect to database
print("[CLI]: Connecting to database...")
metadata_db = DatabaseHandler()

# Initiate camera
print("[CLI]: Initiating cameras...")
camera_controller = CameraController()

# Initiate analysis packages
recognition_controller = RecognitionController()
horizon_tracker_controller = HorizonTrackerController()

# Read packet data
received_data = client_socket.recv(1024).decode()

# Parse data for a command string
print(f"[CLI]: Parsing {received_data}...")
parsed = received_data.split("|")
command = parsed[0]

# 
match command:
    case "STD_CAPTURE":
        camera_select = parsed[1]
        request_epoch = parsed[2]
        resolution = parsed[3] if parsed[3] is not None else None
        camera_controller.capture(camera_select, request_epoch, resolution)
    case "RETRIEVE":
        arguments = parsed[1:]
        database_handler.retrieve(arguments)
    case "RECOGNIZE":
        image_id = parsed[1] # you're welcome to change this if you want to implement it differently
        # argument2 = ...
        recognition_controller.recognize(image_id)
    case "HORIZON":
        image_id = parsed[1] # you're welcome to change this if you want to implement it differently
        # argument2 = ...
        horizon_tracker_controller.detect(image_id)
    case _:
        print(f"[CLI] Unrecognized command: {command}")