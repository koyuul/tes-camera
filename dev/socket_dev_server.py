import socket
import sys
import signal
from datetime import datetime, timezone

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 8080))

server_socket.listen(1)

def handle_exit(signal_num, frame):
    print("\nShutting down gracefully...")
    server_socket.close()
    sys.exit(0)

# Link handle_exit to run on ctrl+c
signal.signal(signal.SIGINT, handle_exit)

while True:
    print("[SERV]: Looking for clients...")
    client_socket, client_address = server_socket.accept()
    received_data = client_socket.recv(1024)
    received_data = received_data.decode()
    print(f"[CLI]: {received_data}")

    if (received_data == "CONNECTION_SUCCESS"):
        now = int(datetime.now(tz=timezone.utc).timestamp())
        command_string = f"STD_CAPTURE|1110|{now}|320x240"
        # command_string = f"RETRIEVE|image_id|19"
        print(f"[SERV]: Sending {command_string}")
        client_socket.send(command_string.encode())
        client_socket.close()
