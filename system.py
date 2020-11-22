

# This class handles the coordination of the boards functions
import ujson
import network
import ntptime
from time import sleep, time
from datauploader import DataUploader
from devicehandler import DeviceHandler
from logger import Logger
class System:

    ESP_LOG_FILE = "esp_log.txt"
    MAX_CONNECT_ATTEMPTS = 10
    # Rate in seconds at whcih data will be uploaded
    UPLOAD_FREQUENCY = 180

    def __init__(self, config_file="config.json"):
        self.logger = Logger(self.ESP_LOG_FILE)
        f = open(config_file)
        self.configs = ujson.load(f)
        self.logger.log("Configs loaded")
        self.device_handler = DeviceHandler(self.configs)
        self.data_uploader = DataUploader()
        self.error_flag = 0

    def connect_wifi(self):
        ssid = self.configs["ssid"]
        password = self.configs["password"]

        station = network.WLAN(network.STA_IF)
        if station.isconnected():
            self.logger.log("Already connected")
            return

        station.active(True)
        station.connect(ssid, password)

        # Loop to wait for station connection
        connect_attempts = 0
        while not station.isconnected() and connect_attempts < self.MAX_CONNECT_ATTEMPTS:
            connect_attempts += 1
            sleep(1)
        if connect_attempts >= self.MAX_CONNECT_ATTEMPTS:
            self.logger.log("Failed to connect to wifi")
            self.error_flag = 1
            return

        self.logger.log("Connection successful")
        self.logger.log(str(station.ifconfig()))

    def start(self):
        self.connect_wifi()
        ntptime.settime()
        self.device_handler.set_initial_state()
    
    def run(self):
        self.start()
        while self.error_flag == 0:
            start_time = time()
            if self.configs["esp_type"]["solenoids"]:
                self.device_handler.open_close_solenoids()
            if self.configs["esp_type"]["data_reader"]:
                data = self.device_handler.read_all_data()
            if self.configs["esp_type"]["data_uploader"]:
                self.data_uploader.upload_data(data)
            if self.configs["esp_type"]["pump"]:
                self.device_handler.check_pump()
            if self.configs["esp_type"]["lights"]:
                 self.device_handler.check_lights()
        # This allows us to always upload at exactly the UPLOAD_FREQUENCY cadence
            time.sleep(self.UPLOAD_FREQUENCY - (time() - start_time) % self.UPLOAD_FREQUENCY)
        self.logger.log("Process stopped")
     
    def test_pump(self):
        self.device_handler.test_pump()
    
    def test_solenoids(self):
        self.device_handler.test_solenoids()
     
    def test_ec(self):
        ec, ppm = self.device_handler.read_ec()
        print("EC: " + str(ec) + " PPM: " + str(ppm))
      
    def test_ph(self):
        pH = self.device_handler.read_ph()
        print("pH: " + str(pH))
      
    def test_pressure(self):
          pressure = self.device_handler.read_pressure()
          print("Pressure: " + str(pressure))
    
    def test_ds18b20(self, pin_name):
          temp = self.device_handler.read_ds18b20(pin_name)
          print(temp)
        
    def turn_off_pump(self):
        self.device_handler.turn_off_pump()
    
    def turn_on_pump(self):
        self.device_handler.turn_on_pump()
    
    def close_solenoids(self):
        self.device_handler.close_solenoids()
    
    def open_solenoids(self):
        self.device_handler.open_solenoids()
    
    def lights_on(self):
        self.device_handler.lights_off()
    
    def lights_off(self):
        self.device_handler.lights_on()
    
    def upper_outer_on(self):
        self.device_handler.upper_outer_on()
    
    def upper_outer_off(self):
        self.device_handler.upper_outer_off()
        
    def upper_inner_on(self):
        self.device_handler.upper_inner_on()
    
    def upper_inner_off(self):
        self.device_handler.upper_inner_off()
        
    def lower_outer_on(self):
        self.device_handler.lower_outer_on()
    
    def lower_outer_off(self):
        self.device_handler.lower_outer_off()
        
    def lower_inner_on(self):
        self.device_handler.lower_inner_on()
    
    def lower_inner_off(self):
        self.device_handler.lower_inner_off()
        
        
    def s_upper_left_on(self):
        self.device_handler.s_upper_left_on()
    
    def s_upper_left_off(self):
        self.device_handler.s_upper_left_off()
        
    def s_upper_right_on(self):
        self.device_handler.s_upper_right_on()
    
    def s_upper_right_off(self):
        self.device_handler.s_upper_right_off()
        
    def s_lower_left_on(self):
        self.device_handler.s_lower_left_on()
    
    def s_lower_left_off(self):
        self.device_handler.s_lower_left_off()
        
    def s_lower_right_on(self):
        self.device_handler.s_lower_right_on()
    
    def s_lower_right_off(self):
        self.device_handler.s_lower_right_off()



