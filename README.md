# tes-camera
SJSU 2024-25 CMPE/SE Senior Project - TES camera board and ML image processing

## todo
- test UART
- add config usage
- flesh out querying
- do a final update on commands

## purpose
This codebase is meant to host the files required to operate the TES camera board. The user notes below detail the hardware setup, and the operational use cases can found on the GitHub Repo Wiki. If there are any confusions at all don't hesitate to reach out!

## usage
The main entry point for this project is the `./main.py`, which is set up and ran by `./startup.sh`. Please see the setup guide above to ensure things are properly set up. 

This repository was designed to model an application that would run on the main MCU, and interface with the ESP-32S via either UART or WiFi. Therefore, I expect there to be some effort required to modify `./main.py` to fit whatever pre-existing system it would fit into (ie altering how input is sent in/received)

In `./main.py`, a input-feedback loop is established, where the script expects commands to be written to the application via the command line. In testing, `./main.py` was ran in a terminal while SSH'd into the host device -- like mentioned above, this is probably different from what the end case would be, it's more of a starter/demo file.

If you're running `./main.py` from the host device, you will be prompted to enter commands in the terminal. Example commands include:
- `CAPTURE:111,320x240` - Capture images from all three cameras with a 10 second timeout.

## hardware overview

### client (ESP-32S)
- The client device runs from an ESP-32S that is hooked up to three ArduCam MEGA 3MP cameras. 
  - The client requires a host device (section below), which sends text based commands.
- Client runs code within the `/esp32` folder. 
- In a nutshell, it's set up to listen over UART/WiFi respond to text commands of a specific format. From those commands, it can capture images, query messages, and set default settings.

### host (RPi5, or any Linux device)
- This codebase was tested with a Raspberry Pi 5, connected via UART/WiFi to an ESP-32s.
- The host device can be replaced with any Linux device, provided the device can wire to an ESP-32S via UART/WiFi, and host it's own hot spot. 
- Host code is in the root directory of this project. It manages communication with the client, and image metadata/storage.

## getting started
### prerequisites
- Raspberry Pi 5 or compatible host, flashed and running Python 3.8+, and using `nmcli` for network mgmt.
- ESP-32S w/ ArduCam MEGA 3MP cameras wired in.

### setup 
[!IMPORTANT]
> TES NOTE: This is for a fresh install, when handed off these steps will already have been completed. 
> These steps may be useful when porting the host app to the host device of your choosing (BAMBI?)

- Host device: (RPi5 or compatible host):
  - Connecting to the RPi 5 demo device:
    - The RPi5 demo device is set up to have a static IP, for development purposes you can SSH into it by:
      - Connect the RPi5 to your computer via ethernet
      - Connect via SSH (I recommend VS code remote explorer) with `ssh tes@192.168.2.2`
    - Wire UART TX/RX, and GND from ESP32 pins to based on `./include/config.json`
      - For the demo device, this will be pins 6 (GND, black), 8 (TX, green), and 10 (RX, blue).
  - `nmcli` is used in `./startup.sh` to create and teardown a fresh hotspot connection for the ESP-32S to look for. If you're using a different network management, alter `./startup.sh`'s "Set Up WiFi hotspot" section.
    - If not using `nmcli`, ensure hotspot settings, SSID, and password match `./include/config.json`.
    - Can test connection using `wifi_test.py` and `uart_test.py`.
  - Clone this repository to the root directory.
  - Create a python `venv` in the root directory
    - If your system doesn't use virtual environments, modify `./startup.sh`'s "Source venv" section.
  - Once venv is created and entered (by running `source ./venv/bin/activate`), pip install the `./requirements.txt` file (by running `pip3 install -r ./requirements.txt`)
  - Set up is complete, you can now run `./startup.sh`. The script is pretty easy to read/tell what's going on, but in a nutshell this script will remove/reset any Linux processes (sockets, hotspot, database) then run `./main.py`. 
    - Again, feel free to modify this script to work for your use case, and reach out to me if there is any confusion.

- Client device
  - Client device setup will only occur if you're re-making this project. 
  - Flash micropython onto an ESP-32S following this guide: https://docs.micropython.org/en/latest/esp32/tutorial/intro.html
  - Wire according to the wiring diagram shared in Google Drive (if you don't have the link, message me on the off chance you're actually remaking it :P)
