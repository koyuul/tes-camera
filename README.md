# tes-camera
SJSU 2024-25 CMPE/SE Senior Project - TES camera board and ML image processing

## user notes
TODO: Format this later...
- How to connect:
  - plug board into power source (not reccomended to power by PC USB port. use a good phone charger)
  - follow the [coral docs](https://coral.ai/docs/dev-board/get-started) to download Mendel
  - connect coral board to the same wifi as your PC. i had issues getting it to run following the user docs, so I just plugged in a m+kb and monitor to manually connect the wifi.
  - run `mdt shell` -- may require multiple times to detect the device, but once it does it should open an ssh terminal.
- Connect via ssh / vscode
  - obtain current IP of the board (last known ip: `10.0.0.214`)
  - if needed, add your ssh key to the board's `~/.ssh/authorized_keys` file.
    - generate/retrieve your own ssh key, then paste the .pub into a new file `~/.ssh/authorized_keysN`, where N = the next available file number (eg authorized_keys1, authorized_keys2, authorized_keys3, ...)
  - once added, you can connect by typing `ssh mendel@[ YOUR IP HERE ]`, eg `ssh mendel@10.0.0.214`
  - you can use the remote explorer extension on vscode to open the system as a vscode project. download the extension on vscode and create a new ssh remote and use the ssh command above
    - i reccomend to try connecting thru mdt first, then ssh in console, then connect in vscode
- How to build / generate / run files:
  - Run the commands in this setting
    - `cd build`
    - `cmake ..`
    - `cd ..`
    - `./build/bin/tes-camera`