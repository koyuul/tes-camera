# tes-camera
SJSU 2024-25 CMPE/SE Senior Project - TES camera board and ML image processing

## purpose
- This codebase is meant to host the files required to operate the TES camera board. The user notes below detail the hardware setup, and the operational use cases can found on the GitHUb Repo Wiki

## user notes
- Overview:
  - Raspberry Pi 5 connects to an ESP-32S, which controls 3 ArduCam MEGA 3MP cameras
    - Raspberry Pi can be replaced with any Linux device, provided the device can connect via UART
- How to connect (to ready-made board):
  - Plug RPi5 into power source (not reccomended to power by PC USB port. use the RPi power adapter or a laptop charger)
  - Power on ESP32, either through the RPi5's power pins, or by it's own power source.
  - Follow directions to connect for your usecase:
    - Connect via ssh / vscode (for development)
      - If connecting to a new network: connect the RPi5 to the local WiFi first, either by manually adding the details onto the SD card, or by plugging in the HDMI cable
      - once added, you can connect by typing `ssh imager@imager.local`
      - If you're running into issues, you can potentially use an Ethernet cable from the RPi5 into your device to SSH
      - you can use the remote explorer extension on vscode to open the system as a vscode project. download the extension on vscode and create a new ssh remote and use the ssh command above
    - Connect via UART
      - Follow the wiring diagram in the documentation.
- Use cases
  - Please refer to the Wiki on GitHub for command documentation
