import socket
import time
from include.database_handler import DatabaseHandler
from include.camera_controller import CameraController

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

received_data = client_socket.recv(1024).decode()
print(f"[CLI]: Parsing {received_data}...")
parsed = received_data.split("|")
command = parsed[0]

if (command == "STD_CAPTURE"):
    camera_select = parsed[1]
    request_epoch = parsed[2]
    resolution = parsed[3] if parsed[3] is not None else None
    camera_controller.capture(camera_select, request_epoch, resolution)
elif (command == "RETRIEVE"):
    arguments = parsed[1:]
    database_handler.retrieve(arguments)
    