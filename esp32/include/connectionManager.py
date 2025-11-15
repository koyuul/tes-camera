from machine import UART
import ujson
import network
import time
import socket

""" ConnectionManager class
    Purpose: Provide methods to ping/manage the WiFi and UART connections to the SFC, and communicate with the SFC.
    Usage: Used by main.py communicate with the SFC and send back any telemetry/images.
    Notes: Please ensure config.json has the correct settings in the "wifi" section
"""
class ConnectionManager:
    def __init__(self):
        # Load config JSON
        with open("config.json", "r") as file:
            config = ujson.load(file)
            self.wifi_config = config["wifi"]
            self.uart_config = config["uart"]
        
        self.wifiEnabled = False
        self.wifi_socket = None
        self.uartEnabled = False

    """
        Initialize the connection to host's WiFi.
        Returns a ping code
    """
    def initHostWifi(self):
        self.wlan = network.WLAN(network.STA_IF)
        
        # Restart the ESP32's WiFi module to clear any previous state
        self.wlan.active(False)
        time.sleep(1)
        self.wlan.active(True)
        time.sleep(1)

        self.wlan.connect(self.wifi_config["ssid"], self.wifi_config["password"])
        
        # Wait for connection with timeout
        timeout_start = time.time()
        while not self.wlan.isconnected():
            if time.time() - timeout_start > self.wifi_config["timeout"]:
                print("[wifi]: timeout")
                return 503
            
        print("[wifi]: connected to network")
        
        # create persistent socket
        try:
            self.wifi_socket = socket.socket()
            self.wifi_socket.settimeout(None)
            self.wifi_socket.connect((self.wifi_config["host"], self.wifi_config["port"]))
            self.wifiEnabled = True
            print("[wifi]: Persistent connection established")
            return 200
        except Exception as e:
            print("[wifi]: Failed to connect socket:", e)
            return 503


    """
        Pings the host through WiFi. Waits 10 seconds before giving up
        Returns:
            200 - Success
            503 - Connection error change to UART mode
    """
    def pingHostWifi(self):
        try:
            self.wifi_socket.send(b"PING\n")
            response = self.wifi_socket.recv(1024).strip().decode()
            print("[wifi]: got:", response)
            if response == "ACK:PING":
                return 200
            else:
                return 502
        except Exception as e:
            print("[wifi]: ERROR:", e)
            return 503


    """
        Initialize the connection to host's UART.
        Returns a ping code
    """
    def initHostUART(self):
        self.uart = UART(
            self.uart_config["id"],
            baudrate=self.uart_config["baudrate"],
            tx=self.uart_config["tx"],
            rx=self.uart_config["rx"]
        )
        time.sleep(1)
        print("[uart]: Created")
        
        # If successful ping
        if (self.pingHostUART() == 200):
            self.uartEnabled = True
            return 200
        else:    
            time.sleep(3)
        
        return 503

    """
        Pings the host through UART. Waits 10 seconds before giving up
        Returns:
            200 - Success
            503 - Connection error change to UART mode
    """
    def pingHostUART(self):
        print("[uart]: Writing PING")
        self.uart.write("PING".encode('utf-8') + b'\n')
        self.uart.flush()
        time.sleep(0.05)
        
        print("[uart]: Waiting for response")
        timeout_start = time.time()
        while True:
            if self.uart.any():
                response = self.uart.readline().strip()
                print(response)
                if response == b"ACK:PING":
                    return 200 
            time.sleep(0.1)

            if time.time() - timeout_start > self.uart_config["timeout"]:
                return 503

    """
        Listens for commands from the host.
        Preference: WiFi first (if connected), then UART as backup.
        Blocking call — use inside main loop.
    """
    def listenHost(self):
        # WiFi first
        if self.wifiEnabled and self.wifi_socket:
            try:
                print("[listenHost]: Waiting for WiFi command...")
                data = self.wifi_socket.recv(1024).strip().decode()
                if data:
                    print("[listenHost]: Received command via WiFi:", data)
                    return data
            except Exception as e:
                print("[listenHost]: WiFi connection lost, falling back to UART")
                print(e)
                self.wifi_socket.close()
                self.wifi_socket = None
                self.wifiEnabled = False

        # Fallback to UART
        if self.uartEnabled:
            print("[listenHost]: Listening via UART...")
            timeout_start = time.time()
            while True:
                if self.uart.any():
                    line = self.uart.readline().strip()
                    if line:
                        cmd = line.decode()
                        print("[listenHost]: Received command via UART:", cmd)
                        return cmd
                time.sleep(0.05)
                if time.time() - timeout_start > self.uart_config["timeout"]:
                    print("[listenHost]: UART listen timed out")
                    return None

        print("[listenHost]: No connection enabled, cannot listen")
        return None

    """
        Send command to host with current mode
        Preference: WiFi first (if connected), then UART as backup.
    """
    def sendHost(self, message):
        try:
            if isinstance(message, str):
                data = (message + "\n").encode("utf-8")
            else:
                data = message
            
            if self.mode == "wifi" and self.wifi_socket:
                self.wifi_socket.send(data)
            elif self.mode == "uart" and self.uart:
                self.uart.write(data)
            else:
                print("[error]: No active connection to send message")
        except Exception as e:
            print("[error]: Failed to send response:", e)

