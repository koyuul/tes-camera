import sys
from include.connection_manager import ConnectionManager
from include.esp32_controller import ESP32Controller
from include.database_handler import DatabaseHandler

def run(): #TODO: make this close the socket cleanly
    # Connect to database
    print("[HOST]: Connecting to database...")
    metadata_db = DatabaseHandler("/home/tes/imager/tes-camera/image_info.db")
    print("[HOST]: Database connected successfully!")

    # Confirm ESP32 connection. Send a handshake to wait for connection before continuing.
    print("[HOST]: Connecting to ESP32...")
    conn = ConnectionManager()

    # Request ESP32 connect to cameras. Kept separate in case a camera stops responding and needs to be disabled.
    # print("[HOST]: Connecting ESP32 to cameras...")
    # conn.send("CONNECT:111,320x240")
    # conn.listen()

    # Input loop
    print("[HOST]: Entering input loop...")
    try:
        while (True):
            # Take in input
            command = input("Enter command: ")
            
            # Break down arguments, if any
            args = []
            if ':' in command:
                operation, arg_str = command.split(':', 1)
                args = arg_str.split(',') if arg_str else []

            print(f"[HOST]: Sending command: {command}")
            conn.send(command)
            
            # Prepare for any command responses
            # When sending a capture command, we expect to receive images back, so we organize and save them
            if command.startswith("CAPTURE"):
                # When sending a capture command, we expect to receive images back, so we organize and save them
                print("[HOST]: Receiving image...")
                enable_mask = args[0]
                timeout_seconds = args[1] if len(args) > 1 else 10
                metadata_db.save_images(conn, enable_mask, timeout_seconds)
                print("[HOST]: Image received and saved!")
            else:
                # Read back any responses
                print("[HOST]: Reading response...")
                resp = conn.listen()
                print(f"[HOST]: Received: {resp}")
    finally:
        print("[HOST]: Closing database...")
        metadata_db.close()

if __name__ == "__main__":
    run()