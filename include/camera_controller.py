import board
import busio
import os
import sqlite3
import sys
import threading
from digitalio import DigitalInOut, Direction
from time import sleep
from datetime import datetime, timezone
from include.camera import *

# These pins work for Google Coral. Please refer to your board's pinout and your wiring to match.
# You can also try print(dir(board)) to view what you have.
CLOCK_PIN = board.ECSPI1_SCLK
MISO_PIN = board.ECSPI1_MISO
MOSI_PIN = board.ECSPI1_MOSI
GPIO_PIN_0 = board.GPIO_P37
GPIO_PIN_1 = board.GPIO_P29
GPIO_PIN_2 = board.GPIO_P36

BAUDRATE = 8000000

# refer to camera.py for possible resolutions
USER_RES = '320x240'

class CameraController:
    def __init__(self):
        # Connect to (or create if needed) the metadata database
        self.conn = sqlite3.connect("/home/mendel/tes-camera/image_info.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                main_id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id TEXT,
                image_group INTEGER,
                request_epoch INTEGER,
                capture_epoch INTEGER,
                camera_source INTEGER,
                image_path TEXT,
                location_prediction TEXT, -- This should change based on what location prediction features we do
                has_earth INTEGER, -- SQLite doesnt have integers, so store this as 1=True 0=False
                has_space INTEGER -- SQLite doesnt have integers, so store this as 1=True 0=False,
            )
        ''')
        self.conn.commit()

        self.cameras_init()

    def cameras_init(self):
        # Initiate a connection to the SPI Bus we're using
        spi = busio.SPI(clock=CLOCK_PIN, MISO=MISO_PIN, MOSI=MOSI_PIN)

        # Lock SPI bus before configuring baudrate
        if spi.try_lock():
            try:
                spi.configure(baudrate=BAUDRATE)
            finally:
                spi.unlock()
        else:
            print("[CAMERA]: Could not lock SPI bus") #TODO: handle this error better...
            exit()
        
        # Initializes all chip select pins
        cs0 = DigitalInOut(GPIO_PIN_0)
        cs0.direction = digitalio.Direction.OUTPUT 

        cs1 = DigitalInOut(GPIO_PIN_1)
        cs1.direction = digitalio.Direction.OUTPUT

        cs2 = DigitalInOut(GPIO_PIN_2)
        cs2.direction = digitalio.Direction.OUTPUT

        # Initalize camera objects
        cam0 = Camera(spi, cs0)
        cam0.resolution = USER_RES

        cam1 = Camera(spi, cs1)
        cam1.resolution = USER_RES

        cam2 = Camera(spi, cs2)
        cam2.resolution = USER_RES

        self.cameras = [cam0, cam1, cam2]
    
    def capture(self, camera_select, request_epoch, resolution=None):
        if (resolution is not None):
            for cam in self.cameras:
                cam.resolution = resolution
                print(f"[CAMERA]: Changing resolution to {resolution}")

        previous_image_group = self.cursor.execute("SELECT MAX(image_group) FROM metadata").fetchone()
        image_group = previous_image_group[0]+1 if previous_image_group is not None and previous_image_group[0] is not None else 1
        image_folder = f"{os.path.expanduser('~/images')}/{image_group}"
        os.makedirs(image_folder, exist_ok=True)

        print (f"{camera_select} {request_epoch} {image_group}")
        ts_ci = int(datetime.now(tz=timezone.utc).timestamp())
        self.capture_images(camera_select, request_epoch, image_group, image_folder)
        ts_ci_done = int(datetime.now(tz=timezone.utc).timestamp())
        print(f"[CAMERA]: Time to capture all images: {ts_ci} to {ts_ci_done} {ts_ci_done - ts_ci}")

        thread = threading.Thread(target=self.process_images, args=(camera_select, request_epoch, image_group, image_folder))
        thread.start()

    def capture_images(self, camera_enable_code, request_epoch, image_group, image_folder):
        for i in range(0, len(camera_enable_code)):
            current_flag = camera_enable_code[i]
            if (current_flag == "1"):
                self.cameras[i].capture_jpg()
                capture_epoch = int(datetime.now(tz=timezone.utc).timestamp())
                sleep(0.05)
                image_id = str(image_group) + "_" + str(i)
                image_path = f"{image_folder}/{image_id}.jpg"

                # Enter image metadata into the metadata table.
                self.cursor.execute(
                    "INSERT INTO metadata(image_id, image_group, request_epoch, capture_epoch, camera_source, image_path) VALUES(?, ?, ?, ?, ?, ?)",
                    ( image_id, image_group, request_epoch, capture_epoch, i, image_path)
                )
                self.conn.commit()

                print(f"[CAM{i}]: Capture complete")

    def process_images(self, camera_enable_code, request_epoch, image_group, image_folder): # Capture the image (into the arducam's buffer), and note the time it was taken
        for i in range(0, len(camera_enable_code)):
            current_flag = camera_enable_code[i]
            if (current_flag == "1"):
                ts_ii = int(datetime.now(tz=timezone.utc).timestamp())
                image_id = str(image_group) + "_" + str(i)
                image_path = f"{image_folder}/{image_id}.jpg"
                self.cameras[i].saveJPG(image_path)
                print(f"[CAM{i}]: Completed the request received at {request_epoch}. Saved into {image_path}.")
                ts_iif = int(datetime.now(tz=timezone.utc).timestamp())
                print(f"[CAMERA]: Time to process image {i}: Started at {ts_ii}, finished at {ts_iif} = {ts_iif - ts_ii}")

