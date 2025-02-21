import time
import os
import json
import board
import busio
import digitalio

'''
Start this alongside the camera module to save photos in a folder with a filename i.e. image-<counter>.jpg
* appends '_' after a word, the next number and the file format
'''
class FileManager:
    def __init__(self, file_manager_name='filemanager.log'):
        
        self.FILE_MANAGER_LOG_NAME = file_manager_name
        self.last_request_filename = None
        file_dict = {}

        # Ensure file is present
        if self.FILE_MANAGER_LOG_NAME not in os.listdir():
            with open(self.FILE_MANAGER_LOG_NAME, 'w') as f:
                json.dump(file_dict, f)
            
        # Check if the filename already exists in the storage
        with open(self.FILE_MANAGER_LOG_NAME, 'r') as f:
            self.file_dict = json.load(f)


    def new_jpg_fn(self, requested_filename=None):
        return (self.new_filename(requested_filename) + '.jpg')
    
    def new_filename(self, requested_filename):
        count = 0
        self.last_request_filename = requested_filename
        
        if requested_filename is None and self.last_request_filename is None:
            raise Exception('Please enter a filename for the first use of the function')
        
        if requested_filename in self.file_dict:
            count = self.file_dict[requested_filename] + 1
        self.file_dict[requested_filename] = count
        
        self.save_manager_file()
        new_filename = f"{requested_filename}_{count}" if count > 0 else f"{requested_filename}"
        
        return new_filename
    
    def save_manager_file(self):
        # Save the updated list back to the storage
        with open(self.FILE_MANAGER_LOG_NAME, 'w') as f:
            json.dump(self.file_dict, f)



class Camera:
    ## For camera Reset
    CAM_REG_SENSOR_RESET = 0x07
    CAM_SENSOR_RESET_ENABLE = 0x40
    
    ## For get_sensor_config
    CAM_REG_SENSOR_ID = 0x40
    
    SENSOR_5MP_1 = 0x81
    SENSOR_3MP_1 = 0x82
    SENSOR_5MP_2 = 0x83
    SENSOR_3MP_2 = 0x84
    
    # Set Colour Effect
    CAM_REG_COLOR_EFFECT_CONTROL = 0x27
    
    SPECIAL_NORMAL = 0x00
    SPECIAL_COOL = 1
    SPECIAL_WARM = 2
    SPECIAL_BW = 0x04
    SPECIAL_YELLOWING = 4
    SPECIAL_REVERSE = 5
    SPECIAL_GREENISH = 6
    SPECIAL_LIGHT_YELLOW = 9 # 3MP Only


    # Set Brightness
    CAM_REG_BRIGHTNESS_CONTROL = 0X22

    BRIGHTNESS_MINUS_4 = 8
    BRIGHTNESS_MINUS_3 = 6
    BRIGHTNESS_MINUS_2 = 4
    BRIGHTNESS_MINUS_1 = 2
    BRIGHTNESS_DEFAULT = 0
    BRIGHTNESS_PLUS_1 = 1
    BRIGHTNESS_PLUS_2 = 3
    BRIGHTNESS_PLUS_3 = 5
    BRIGHTNESS_PLUS_4 = 7


    # Set Contrast
    CAM_REG_CONTRAST_CONTROL = 0X23

    CONTRAST_MINUS_3 = 6
    CONTRAST_MINUS_2 = 4
    CONTRAST_MINUS_1 = 2
    CONTRAST_DEFAULT = 0
    CONTRAST_PLUS_1 = 1
    CONTRAST_PLUS_2 = 3
    CONTRAST_PLUS_3 = 5


    # Set Saturation
    CAM_REG_SATURATION_CONTROL = 0X24

    SATURATION_MINUS_3 = 6
    SATURATION_MINUS_2 = 4
    SATURATION_MINUS_1 = 2
    SATURATION_DEFAULT = 0
    SATURATION_PLUS_1 = 1
    SATURATION_PLUS_2 = 3
    SATURATION_PLUS_3 = 5


    # Set Exposure Value
    CAM_REG_EXPOSURE_CONTROL = 0X25

    EXPOSURE_MINUS_3 = 6
    EXPOSURE_MINUS_2 = 4
    EXPOSURE_MINUS_1 = 2
    EXPOSURE_DEFAULT = 0
    EXPOSURE_PLUS_1 = 1
    EXPOSURE_PLUS_2 = 3
    EXPOSURE_PLUS_3 = 5
    
    
    # Set Whitebalance
    CAM_REG_WB_MODE_CONTROL = 0X26
    
    WB_MODE_AUTO = 0
    WB_MODE_SUNNY = 1
    WB_MODE_OFFICE = 2
    WB_MODE_CLOUDY = 3
    WB_MODE_HOME = 4

    # Set Sharpness
    CAM_REG_SHARPNESS_CONTROL = 0X28 #3MP only
    
    SHARPNESS_NORMAL = 0
    SHARPNESS_1 = 1
    SHARPNESS_2 = 2
    SHARPNESS_3 = 3
    SHARPNESS_4 = 4
    SHARPNESS_5 = 5
    SHARPNESS_6 = 6
    SHARPNESS_7 = 7
    SHARPNESS_8 = 8
    
    # Set Autofocus
    CAM_REG_AUTO_FOCUS_CONTROL = 0X29 #5MP only

    # Set Image quality
    CAM_REG_IMAGE_QUALITY = 0x2A
    
    IMAGE_QUALITY_HIGH = 0
    IMAGE_QUALITY_MEDI = 1
    IMAGE_QUALITY_LOW = 2
    
    # Manual gain, and exposure are explored in the datasheet - https://www.arducam.com/downloads/datasheet/Arducam_MEGA_SPI_Camera_Application_Note.pdf

    # Device addressing
    CAM_REG_DEBUG_DEVICE_ADDRESS = 0x0A
    deviceAddress = 0x78
    
    # For Waiting
    CAM_REG_SENSOR_STATE = 0x44
    CAM_REG_SENSOR_STATE_IDLE = 0x01
    
    # Setup for capturing photos
    CAM_REG_FORMAT = 0x20
    
    CAM_IMAGE_PIX_FMT_JPG = 0x01
    CAM_IMAGE_PIX_FMT_RGB565 = 0x02
    CAM_IMAGE_PIX_FMT_YUV = 0x03
    
    # Resolution settings
    CAM_REG_CAPTURE_RESOLUTION = 0x21

    # Some resolutions are not available - refer to datasheet https://www.arducam.com/downloads/datasheet/Arducam_MEGA_SPI_Camera_Application_Note.pdf
    RESOLUTION_320X240 = 0X01
    RESOLUTION_640X480 = 0X02
    RESOLUTION_1280X720 = 0X04
    RESOLUTION_1600X1200 = 0X06
    RESOLUTION_1920X1080 = 0X07
    RESOLUTION_2048X1536 = 0X08 # 3MP only
    RESOLUTION_2592X1944 = 0X09 # 5MP only
    RESOLUTION_96X96 = 0X0a
    RESOLUTION_128X128 = 0X0b
    RESOLUTION_320X320 = 0X0c
    
    valid_3mp_resolutions = {
        '320x240': RESOLUTION_320X240, 
        '640x480': RESOLUTION_640X480, 
        '1280x720': RESOLUTION_1280X720, 
        '1600x1200': RESOLUTION_1600X1200,
        '1920x1080': RESOLUTION_1920X1080,
        '2048x1536': RESOLUTION_2048X1536,
        '96X96': RESOLUTION_96X96,
        '128X128': RESOLUTION_128X128,
        '320X320': RESOLUTION_320X320
    }

    valid_5mp_resolutions = {
        '320x240': RESOLUTION_320X240, 
        '640x480': RESOLUTION_640X480, 
        '1280x720': RESOLUTION_1280X720, 
        '1600x1200': RESOLUTION_1600X1200,
        '1920x1080': RESOLUTION_1920X1080,
        '2592x1944': RESOLUTION_2592X1944,
        '96X96': RESOLUTION_96X96,
        '128X128': RESOLUTION_128X128,
        '320X320': RESOLUTION_320X320
    }

    # FIFO and State setting registers
    ARDUCHIP_FIFO = 0x04
    FIFO_CLEAR_ID_MASK = 0x01
    FIFO_START_MASK = 0x02
    
    ARDUCHIP_TRIG = 0x44
    CAP_DONE_MASK = 0x04
    
    FIFO_SIZE1 = 0x45
    FIFO_SIZE2 = 0x46
    FIFO_SIZE3 = 0x47
    
    SINGLE_FIFO_READ = 0x3D
    BURST_FIFO_READ = 0X3C
    
    # Size of image_buffer (Burst reading)
    BUFFER_MAX_LENGTH = 255
    
    # For 5MP startup routine
    WHITE_BALANCE_WAIT_TIME_MS = 500


# User callable functions
## Main functions
## Setting functions
# Internal functions
## High level internal functions
## Low level

##################### Callable FUNCTIONS #####################

########### CORE PHOTO FUNCTIONS ###########
    def __init__(self, spi_bus, cs, skip_sleep=False, debug_information=False):
        self.cs = cs
        self.cs.value=True
        self.spi_bus = spi_bus
        self.debug_information = debug_information

        self._write_reg(self.CAM_REG_SENSOR_RESET, self.CAM_SENSOR_RESET_ENABLE) # Reset camera
        self._wait_idle()
        self._get_sensor_config() # Get camera sensor information
        self._wait_idle()
        self._write_reg(self.CAM_REG_DEBUG_DEVICE_ADDRESS, self.deviceAddress)
        self._wait_idle()

        self.run_start_up_config = True

        # Set default format and resolution
        self.current_pixel_format = self.CAM_IMAGE_PIX_FMT_JPG
        self.old_pixel_format = self.current_pixel_format
        
        self.current_resolution_setting = self.RESOLUTION_640X480 # ArduCam driver defines this as mode
        self.old_resolution = self.current_resolution_setting
        
        
        self.set_filter(self.SPECIAL_NORMAL)
        
        self.received_length = 0
        self.total_length = 0
        
        # Burst setup
        self.first_burst_run = False
        self.image_buffer = bytearray(self.BUFFER_MAX_LENGTH)
        self.valid_image_buffer = 0
        
        
        # Tracks the AWB warmup time
        self.start_time = time.monotonic() * 1000  # Use monotonic for timing
        if self.debug_information:
            print('Camera version =', self.camera_idx)
        if self.camera_idx == '3MP':
            self.startup_routine_3MP()
        
        if self.camera_idx == '5MP' and skip_sleep == False:
            utime.sleep_ms(self.WHITE_BALANCE_WAIT_TIME_MS)


    def startup_routine_3MP(self):
        # Leave the shutter open for some time seconds (i.e. take a few photos without saving)
        if self.debug_information:
            print('Running 3MP startup routine') 
        self.capture_jpg()
        self.saveJPG('dummy_image.jpg')
        os.remove('dummy_image.jpg')
        if self.debug_information:
            print('Startup routine complete') 

    '''
    Issue warning if the filepath doesnt end in .jpg (Blank) and append
    Issue error if the filetype is NOT .jpg
    '''
    def capture_jpg(self):
        if (time.monotonic() - self.start_time <= self.WHITE_BALANCE_WAIT_TIME_MS / 1000) and self.camera_idx == '5MP':
            print('Please add a ', self.WHITE_BALANCE_WAIT_TIME_MS, 'ms delay to allow for white balance to run') 
        else:
            # JPG, bmp ect
            if (self.old_pixel_format != self.current_pixel_format) or self.run_start_up_config:
                self.old_pixel_format = self.current_pixel_format
                self._write_reg(self.CAM_REG_FORMAT, self.current_pixel_format) # Set to capture a jpg
                self._wait_idle()
            if (self.old_resolution != self.current_resolution_setting) or self.run_start_up_config:
                self.old_resolution = self.current_resolution_setting
                self._write_reg(self.CAM_REG_CAPTURE_RESOLUTION, self.current_resolution_setting)
                if self.debug_information:
                    print('Setting resolution to ', self.current_resolution_setting) 
                self._wait_idle()
            self.run_start_up_config = False
            
            # Start capturing the photo
            self._set_capture()

    def saveJPG(self,filename):
        headflag = 0
        if self.debug_information:
            print('Saving image, please dont remove power') 
        
        image_data = 0x00
        image_data_next = 0x00
        
        image_data_int = 0x00
        image_data_next_int = 0x00

        if self.debug_information:
            print("Image length: ", self.received_length) 
        start_time = time.time()
        while(self.received_length):
            image_data = image_data_next
            image_data_int = image_data_next_int
            
            image_data_next = self._read_byte()
            image_data_next_int = image_data_next # TODO: CHANGE TO READ n BYTES
            
            if headflag == 1:
                jpg_to_write.write(bytes([image_data_next]))
            
            if (image_data_int == 0xff) and (image_data_next_int == 0xd8):
                headflag = 1
                jpg_to_write = open(filename,'wb')
                jpg_to_write.write(bytes([image_data]))
                jpg_to_write.write(bytes([image_data_next]))
                
            if (image_data_int == 0xff) and (image_data_next_int == 0xd9):
                headflag = 0
                jpg_to_write.write(bytes([image_data_next]))
                jpg_to_write.close()
                if self.debug_information:
                    print(f"Save at {filename} complete, took {time.time() - start_time:.4f} seconds to save image") 
                return

    @property
    def resolution(self):
        return self.current_resolution_setting

    @resolution.setter
    def resolution(self, new_resolution):
        if self.debug_information:
            print("Updating resolution to " + new_resolution) 
            print(self.camera_idx) 
        input_string_lower = new_resolution.lower()
        if self.camera_idx == '3MP':
            if input_string_lower in self.valid_3mp_resolutions:
                if self.debug_information:
                    print(self.current_resolution_setting) 
                self.current_resolution_setting = self.valid_3mp_resolutions[input_string_lower]
                if self.debug_information:
                    print(self.current_resolution_setting) 

            else:
                raise ValueError("Invalid resolution provided for {}, please select from {}".format(self.camera_idx, list(self.valid_3mp_resolutions.keys())))
        
        elif self.camera_idx == '5MP':
            if input_string_lower in self.valid_5mp_resolutions:
                self.current_resolution_setting = self.valid_5mp_resolutions[input_string_lower]
            else:
                raise ValueError("Invalid resolution provided for {}, please select from {}".format(self.camera_idx, list(self.valid_5mp_resolutions.keys())))
    

    def set_pixel_format(self, new_pixel_format):
        self.current_pixel_format = new_pixel_format

########### ACCSESSORY FUNCTIONS ###########

    # TODO: Complete for other camera settings
    # Make these setters - https://github.com/CoreElectronics/CE-PiicoDev-Accelerometer-LIS3DH-MicroPython-Module/blob/abcb4337020434af010f2325b061e694b808316d/PiicoDev_LIS3DH.py#L118C1-L118C1
    
#     # Set Brightness
#     CAM_REG_BRIGHTNESS_CONTROL = 0X22
# 
#     BRIGHTNESS_MINUS_4 = 8
#     BRIGHTNESS_MINUS_3 = 6
#     BRIGHTNESS_MINUS_2 = 4
#     BRIGHTNESS_MINUS_1 = 2
#     BRIGHTNESS_DEFAULT = 0
#     BRIGHTNESS_PLUS_1 = 1
#     BRIGHTNESS_PLUS_2 = 3
#     BRIGHTNESS_PLUS_3 = 5
#     BRIGHTNESS_PLUS_4 = 7


    def set_brightness_level(self, brightness):
        self._write_reg(self.CAM_REG_BRIGHTNESS_CONTROL, brightness)
        self._wait_idle()

    def set_filter(self, effect):
        self._write_reg(self.CAM_REG_COLOR_EFFECT_CONTROL, effect)
        self._wait_idle()

#     # Set Saturation
#     CAM_REG_SATURATION_CONTROL = 0X24
# 
#     SATURATION_MINUS_3 = 6
#     SATURATION_MINUS_2 = 4
#     SATURATION_MINUS_1 = 2
#     SATURATION_DEFAULT = 0
#     SATURATION_PLUS_1 = 1
#     SATURATION_PLUS_2 = 3
#     SATURATION_PLUS_3 = 5

    def set_saturation_control(self, saturation_value):
        self._write_reg(self.CAM_REG_SATURATION_CONTROL, saturation_value)
        self._wait_idle()

#     # Set Exposure Value
#     CAM_REG_EXPOSURE_CONTROL = 0X25
# 
#     EXPOSURE_MINUS_3 = 6
#     EXPOSURE_MINUS_2 = 4
#     EXPOSURE_MINUS_1 = 2
#     EXPOSURE_DEFAULT = 0
#     EXPOSURE_PLUS_1 = 1
#     EXPOSURE_PLUS_2 = 3
#     EXPOSURE_PLUS_3 = 5


#     # Set Contrast
#     CAM_REG_CONTRAST_CONTROL = 0X23
# 
#     CONTRAST_MINUS_3 = 6
#     CONTRAST_MINUS_2 = 4
#     CONTRAST_MINUS_1 = 2
#     CONTRAST_DEFAULT = 0
#     CONTRAST_PLUS_1 = 1
#     CONTRAST_PLUS_2 = 3
#     CONTRAST_PLUS_3 = 5

    def set_contrast(self, contrast):
        self._write_reg(self.CAM_REG_CONTRAST_CONTROL, contrast)
        self._wait_idle()


    def set_white_balance(self, environment):
        register_value = self.WB_MODE_AUTO

        if environment == 'sunny':
            register_value = self.WB_MODE_SUNNY
        elif environment == 'office':
            register_value = self.WB_MODE_OFFICE
        elif environment == 'cloudy':
            register_value = self.WB_MODE_CLOUDY
        elif environment == 'home':
            register_value = self.WB_MODE_HOME
        elif self.camera_idx == '3MP':
            if self.debug_information:
                print('TODO UPDATE: For best results set a White Balance setting') 

        self.white_balance_mode = register_value
        self._write_reg(self.CAM_REG_WB_MODE_CONTROL, register_value)
        self._wait_idle()
    
    def activate_camera(self):
        self.cs.value = False
    
    def deactivate_camera(self):
        self.cs.value = True

##################### INTERNAL FUNCTIONS - HIGH LEVEL #####################

########### CORE PHOTO FUNCTIONS ###########
    def _clear_fifo_flag(self):
        self._write_reg(self.ARDUCHIP_FIFO, self.FIFO_CLEAR_ID_MASK)

    def _start_capture(self):
        self._write_reg(self.ARDUCHIP_FIFO, self.FIFO_START_MASK)

    def _set_capture(self):
        if self.debug_information:
            print('Starting capture JPG') 
        start_time = time.time()
        self._clear_fifo_flag()
        self._wait_idle()
        self._start_capture()
        while (int(self._get_bit(self.ARDUCHIP_TRIG, self.CAP_DONE_MASK)) == 0):
            time.sleep(0.2)
        self.received_length = self._read_fifo_length()
        self.total_length = self.received_length
        self.burst_first_flag = False
        if self.debug_information:
            print(f"Capture complete, took {time.time() - start_time:.4f} seconds to save image") 
    
    def _read_fifo_length(self): # TODO: CONFIRM AND SWAP TO A 3 BYTE READ
        len1 = self._read_reg(self.FIFO_SIZE1)
        len2 = self._read_reg(self.FIFO_SIZE2)
        len3 = self._read_reg(self.FIFO_SIZE3)
        return ((len3 << 16) | (len2 << 8) | len1) & 0xffffff

    def _get_sensor_config(self):
        camera_id = self._read_reg(self.CAM_REG_SENSOR_ID)
        # print(type(camera_id), camera_id)  # Debugging line
        self._wait_idle()
        if (camera_id == self.SENSOR_3MP_1) or (camera_id == self.SENSOR_3MP_2):
            self.camera_idx = '3MP'
        if (camera_id == self.SENSOR_5MP_1) or (camera_id == self.SENSOR_5MP_2):
            self.camera_idx = '5MP'


##################### INTERNAL FUNCTIONS - LOW LEVEL #####################

    def _read_buffer(self):
        if self.debug_information:
            print('COMPLETE') 

    def _bus_write(self, addr, val):
        self.cs.value = False
        self.spi_bus.write(bytes([addr]))
        self.spi_bus.write(bytes([val])) # FixMe only works with single bytes
        self.cs.value = True
        time.sleep(0.001) # From the Arducam Library
        return 1
    
    def _bus_read(self, addr):
        self.cs.value = False
        self.spi_bus.write(bytes([addr]))

        buffer = bytearray(2)
        data = self.spi_bus.readinto(buffer) # Only read second set of data
        self.cs.value = True
        return buffer[1]

    def _write_reg(self, addr, val):
        self._bus_write(addr | 0x80, val)

    def _read_reg(self, addr):
        data = self._bus_read(addr & 0x7F)
        return data # TODO: Check that this should return raw bytes or int (int.from_bytes(data, 1))

    def _read_byte(self):
        self.cs.value = False  # Pull CS low to select the device
        self.spi_bus.write(bytes([self.SINGLE_FIFO_READ]))  # Send the read command

        # Read the first dummy byte
        dummy_buffer = bytearray(1)
        self.spi_bus.readinto(dummy_buffer)  # Read a dummy byte to receive the response

        # Now read the actual byte
        data_buffer = bytearray(1)
        self.spi_bus.readinto(data_buffer)  # Read the actual data byte

        self.cs.value = True  # Pull CS high to deselect the device
        self.received_length -= 1  # Decrement the received length
        return data_buffer[0]  # Return the read byte
    
    def _wait_idle(self):
        data = self._read_reg(self.CAM_REG_SENSOR_STATE)
        # Ensure data is in bytes; if itâ€™s not, handle it accordingly
        if isinstance(data, bytes):
            while (int.from_bytes(data, 'little') & 0x03) == self.CAM_REG_SENSOR_STATE_IDLE:
                data = self._read_reg(self.CAM_REG_SENSOR_STATE)
                time.sleep(0.002) # From the Arducam Library
                
        else:
            # If data is not in bytes, just compare it directly
            while (data & 0x03) == self.CAM_REG_SENSOR_STATE_IDLE:
                data = self._read_reg(self.CAM_REG_SENSOR_STATE)
                time.sleep(0.002) # From the Arducam Library

    def _get_bit(self, addr, bit):
        data = self._read_reg(addr);
        return data & bit;


