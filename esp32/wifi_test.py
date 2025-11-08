import network, time, ujson
"""
    Run this code on the ESP32 to test WiFi functionality.
    Check documentation to make sure the host device is hosting
    the hotspot correctly (2.4 GHz, WPA2, etc).
    TODO: Update the documentation.
"""

wlan = network.WLAN(network.STA_IF)

# Restart the ESP32's WiFi module to clear any previous state
wlan.active(False)
time.sleep(1)
wlan.active(True)
time.sleep(1)

# Scan and (roughly) print available networks, make sure the target network is visible
print(wlan.scan())

# Load WiFi credentials from config.json
with open("config.json", "r") as file:
    config = ujson.load(file)
    wifi_config = config["wifi"]
    ssid = wifi_config["ssid"]
    password = wifi_config["password"]

# Connect to the target network
wlan.connect(ssid, password)

# Wait for connection with timeout
timeout_start = time.time()
while not wlan.isconnected():
    print("[wifi status]: ", wlan.status())

    if time.time() - timeout_start > 15:
        print("[wifi]: timeout")
        print(wlan.isconnected())
        break
    time.sleep(1)
