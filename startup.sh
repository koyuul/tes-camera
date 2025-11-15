#!/bin/bash
set -e

# Kill any prevoius processes if rerunning
echo "[Startup] Killing any running Python processes..."
sudo pkill -f /home/imager/tes-camera/main.py || true
echo "[Startup] Waiting for sockets to clear..."
sleep 2

# Remove existing hotspot if present
echo "[Startup] Removing existing hotspot if present..."
sudo nmcli connection delete localhotspot || true

# If --reset-db flag present, delete the database
if [[ "$@" == *"--reset-db"* ]]; then
    echo "[Startup] Deleting image_info.db..."
    rm -f /home/tes/imager/tes-camera/image_info.db
    rm -rf /home/tes/captures/
fi

# Set up WiFi hotspot
echo "[Startup] Setting up WiFi hotspot..."
sudo nmcli connection add type wifi ifname wlan0 con-name localhotspot autoconnect no ssid "pi-flight-cpu"
sudo nmcli connection modify localhotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method manual ipv4.addresses 192.168.50.1/24 wifi-sec.key-mgmt wpa-psk wifi-sec.psk "sjsusjsu"
sudo nmcli connection modify localhotspot 802-11-wireless-security.key-mgmt wpa-psk
sudo nmcli connection modify localhotspot 802-11-wireless-security.proto rsn
sudo nmcli connection modify localhotspot 802-11-wireless-security.pairwise ccmp
sudo nmcli connection modify localhotspot 802-11-wireless-security.group ccmp
sudo nmcli connection up localhotspot

# Source venv
echo "[Startup] Activating Python virtual environment..."
source /home/tes/venv/bin/activate

# Run main
echo "[Startup] Running main application..."
python3 /home/tes/imager/tes-camera/main.py