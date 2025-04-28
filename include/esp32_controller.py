import time

class ESP32Controller:
    def __init__(self, uart_connection):
        self.esp32 = uart_connection

    def get_uart(self):
        return self.esp32    
    
    def send_handshake(self):
        self.send_command("PING")
        start = time.time()
        while time.time() - start < 5:  # timeout in 5 seconds
            if self.esp32.in_waiting:
                line = self.esp32.readline().strip()
                if line == b'PONG':
                    return True
        return False
    
    def send_command(self, command):
        self.esp32.write(command.encode('utf-8') + b'\n')
        self.esp32.flush()
        time.sleep(0.05)
            
    def read_response(self, timeout=5):
        buffer = b''
        start_time = time.time()

        while True:
            if self.esp32.in_waiting:
                byte = self.esp32.read(1)
                if byte:
                    buffer += byte
                    if buffer.endswith(b'\n'):
                        return buffer.strip()
            
            # Check for timeout
            if time.time() - start_time > timeout:
                print("[HOST]: Timeout waiting for response.")
                return "Timeout"

            time.sleep(0.01)  # Be nice to CPU
