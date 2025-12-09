from include.connection_manager import ConnectionManager
from include.database_handler import DatabaseHandler
from include.config_manager import ConfigManager

def run(): #TODO: make this close the socket cleanly
    # Connect to database
    print("[HOST]: Connecting to database...")
    metadata_db = DatabaseHandler("/home/tes/imager/tes-camera/image_info.db")
    print("[HOST]: Database connected successfully!")

    # Confirm ESP32 connection. Send a handshake to wait for connection before continuing.
    print("[HOST]: Connecting to ESP32...")
    conn = ConnectionManager()

    # Initialize configuration manager
    config_manager = ConfigManager()

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

             # Validate enable_mask against config for commands that use it
            if operation in ["CAPTURE", "CONNECT", "SET_RES", "HEALTH_CHK"] and args:
                enable_mask = int(args[0])
                allowed_mask = int(config_manager.get('esp32_config.camera_health', '111'))
                
                # Check if requested mask tries to enable cameras that are disabled in config
                if (enable_mask & ~allowed_mask) != 0:
                    print(f"[HOST]: Error - enable_mask {enable_mask:03b} requests disabled cameras. Allowed: {allowed_mask:03b}")
                    continue

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
            elif command.startswith("EDIT_CONFIG"):
                print("[HOST]: Editing configuration...")
                key = args[0]
                value = args[1]
                success = config_manager.set(key, value)
                if success:
                    print(f"[HOST]: Configuration '{key}' set to '{value}' successfully!")
                else:
                    print(f"[HOST]: Failed to set configuration '{key}'.")
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