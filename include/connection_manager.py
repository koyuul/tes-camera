import socket
import serial
import sys
import time
import json

class ConnectionManager:
    def __init__(self, use_uart=False):
        self.mode = None
        self.wifi_socket = None
        self.uart = None

        # Load config JSON
        with open("config.json", "r") as file:
            config = json.load(file)
            self.wifi_cfg = config["wifi"]
            self.uart_cfg = config["uart"]

        # WiFi by default, uart as manual fallback
        if use_uart:
            print("[Init]: Forcing UART mode")
            if self._init_uart(self.uart_cfg["port"], self.uart_cfg["baudrate"]):
                self.mode = "uart"
                print("[Init]: Using UART mode")
            else:
                print("[Init]: UART failed, try WiFi. Exiting...")
                sys.exit(1)
        else:
            print("[Init]: Trying WiFi first...")
            if self._init_wifi():
                self.mode = "wifi"
                print("[Init]: Using WiFi mode")
            else:
                print("[Init]: WiFi failed, try UART. Exiting...")
                sys.exit(1)

    def _init_wifi(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.wifi_cfg["init_timeout"])
            s.bind((self.wifi_cfg["host"], self.wifi_cfg["port"]))
            s.listen(1)
            conn, addr = s.accept()  # blocks until ESP connects
            self.wifi_socket = conn
            self.mode = "wifi"

            # After initial connect, no timeout limit
            s.settimeout(None)

            # Simple handshake
            self.send("PING")
            resp = self.listen()
            print(resp)
            if resp == "PONG":
                return True

        except Exception as e:
            print(f"[WiFi Error]: {e}")
        return False

    # Read in bytes, used for downloading images
    def read_bytes(self, n=4096, timeout=10):
        start_time = time.time()
        buffer = b""

        if self.mode == "wifi" and self.wifi_socket:
            self.wifi_socket.settimeout(0.5)  # allow repeated checks
            while True:
                try:
                    chunk = self.wifi_socket.recv(n)
                    if chunk:
                        buffer += chunk
                        start_time = time.time()  # reset timeout
                        # Stop if EOF detected
                        if b'EOF' in buffer:
                            return buffer
                    else:
                        # Connection closed
                        break
                except socket.timeout:
                    if time.time() - start_time > timeout:
                        break
            self.wifi_socket.settimeout(None)  # allow repeated checks
            return buffer

        elif self.mode == "uart" and self.uart:
            while True:
                if self.uart.in_waiting:
                    chunk = self.uart.read(n)
                    if chunk:
                        buffer += chunk
                        start_time = time.time()
                        if b'EOF' in buffer:
                            return buffer
                if time.time() - start_time > timeout:
                    break
                time.sleep(0.01)
            return buffer
        return buffer


    def _init_uart(self, port, baud):
        try:
            self.uart = serial.Serial(port, baudrate=baud)
            self.mode = "uart"
            time.sleep(1)

            # Simple handshake
            print("[UART]: waiting for PING")
            ping = self.listen()
            if ping == "PING":
                print("[UART]: got PING, sending PONG")
                self.send("PONG")
                return True
            else:
                print("[UART]: No PING received")
                return False
        except Exception as e:
            print(f"[UART Error]: {e}")
            sys.exit(1)
        return False

    def send(self, message: str):
        try:
            if self.mode == "wifi" and self.wifi_socket:
                self.wifi_socket.sendall(message.encode("utf-8") + b"\n")
            elif self.mode == "uart" and self.uart:
                self.uart.write(message.encode("utf-8") + b"\n")
                self.uart.flush()
            else:
                print("[Error]: No connection available to send message")
        except Exception as e:
            print(f"[Send Error]: {e}")

    def listen(self):
        start = time.time()
        buffer = b""

        if self.mode == "wifi":
            try:
                while True:
                    data = self.wifi_socket.recv(1)
                    if not data:
                        break
                    buffer += data
                    if buffer.endswith(b"\n"):
                        return buffer.strip().decode()
            except Exception as e:
                print(f"[WiFi Listen Error]: {e}")
        elif self.mode == "uart":
            while True:
                if self.uart.in_waiting:
                    byte = self.uart.read(1)
                    buffer += byte
                    if buffer.endswith(b"\n"):
                        return buffer.strip().decode()
                time.sleep(0.01)
        else:
            print("[Listen Error]: No connection available")
            return None