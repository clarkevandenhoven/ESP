# This class handles the coordination of the boards functions
import ujson
import network
import ntptime
import machine
from time import sleep, time
from datauploader import DataUploader
from devicehandler import DeviceHandler
from logger import Logger

class System:

    ESP_LOG_FILE = "esp_log.txt"
    MAX_CONNECT_ATTEMPTS = 50
    # Rate in seconds at whcih data will be uploaded

    def __init__(self, config_file="config.json"):
        self.logger = Logger(self.ESP_LOG_FILE)
        f = open(config_file)
        self.id = str(machine.unique_id())
        self.configs = ujson.load(f)
        self.logger.log("Configs loaded")
        self.device_handler = DeviceHandler(self.configs)
        self.data_uploader = DataUploader()
        self.error_flag = 0

    def connect_wifi(self):
        ssid = self.configs[self.id]["ssid"]
        password = self.configs[self.id]["password"]

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
    
    def retry_fun(self, fun, max_tries=10):
        for i in range(max_tries):
            try:
                sleep(1)
                fun()
                break
            except OSError:
                continue

    def start(self):
        self.connect_wifi()
        self.retry_fun(ntptime.settime)
        self.device_handler.set_initial_state()

    def run(self):
        self.start()
        while self.error_flag == 0:
            start_time = time()
            if self.configs[self.id]["esp_type"]["solenoids"]:
                self.device_handler.open_close_solenoids()
            if self.configs[self.id]["esp_type"]["data_reader"]:
                data = self.device_handler.read_all_data()
            if self.configs[self.id]["esp_type"]["data_uploader"]:
                self.data_uploader.upload_data(data)
            if self.configs[self.id]["esp_type"]["pump"]:
                self.device_handler.check_pump()
            if self.configs[self.id]["esp_type"]["lights"]:
                 self.device_handler.check_lights()
            if self.configs[self.id]["esp_type"]["fans"]:
                 self.device_handler.check_fans()
            if self.configs[self.id]["esp_type"]["water_level"]:
                 self.fill_water()
            if self.configs[self.id]["esp_type"]["nutrient_controller"]:
                 self.fill_all_nutrients()
                 self.fix_ph()
        # This allows us to always upload at exactly the UPLOAD_FREQUENCY cadence
            sleep(self.configs[self.id]["loop_frequency"] - (time() - start_time) % self.configs[self.id]["loop_frequency"])
        self.logger.log("Process stopped")
    
    def fill_water(self):
        water_level = self.device_handler.read_water_level()
        if water_level < 0.6 * self.configs[self.id]["reservoir_height"]:
            self.device_handler.add_water()

    
    def fill_all_nutrients(self):
        self.device_handler.circulation_pump_on()
        for cont in range(1,4):
            self.device_handler.add_nutrient(cont)
        sleep(15)
        self.device_handler.circulation_pump_off()
    
    def fix_ph(self):
        self.device_handler.circulation_pump_on()
        while float(self.device_handler.read_ph()) > 8: 
            self.device_handler.add_nutrient(4)
        while float(self.device_handler.read_ph()) < 5.5:
            self.device_handler.add_nutrient(5)
        sleep(15)
        self.device_handler.circulation_pump_off()
    
    def test_loops(self):
        while True:
            self.device_handler.open_close_solenoids()
            self.device_handler.check_pump()

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

    def test_water_level(self):
        water_level = self.device_handler.read_water_level()
        print("Water level: " + str(water_level))

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

    def fan_upper_on(self):
        self.device_handler.fan_upper_on()

    def fan_upper_off(self):
        self.device_handler.fan_upper_off()

    def fan_lower_on(self):
        self.device_handler.fan_lower_on()

    def fan_lower_off(self):
        self.device_handler.fan_lower_off()

    def set_initial_state(self):
        self.device_handler.set_initial_state()


    def p_pump_on(self):
        self.device_handler.p_pump_on()
   
   
   
    def p_pump1_on(self):
        self.device_handler.p_pump1_on()
    
    def p_pump1_off(self):
        self.device_handler.p_pump1_off()
    
    def p_pump2_on(self):
        self.device_handler.p_pump2_on()
    
    def p_pump2_off(self):
        self.device_handler.p_pump2_off()
    
    def p_pump3_on(self):
        self.device_handler.p_pump3_on()
    
    def p_pump3_off(self):
        self.device_handler.p_pump3_off()
    
    def p_pump4_on(self):
        self.device_handler.p_pump4_on()
    
    def p_pump4_off(self):
        self.device_handler.p_pump4_off()
    
    def p_pump5_on(self):
        self.device_handler.p_pump5_on()
    
    def p_pump5_off(self):
        self.device_handler.p_pump5_off()
   
    def p_pump6_on(self):
        self.device_handler.p_pump6_on()
    
    def p_pump6_off(self):
        self.device_handler.p_pump6_off()
   
    
    def stirrer_on(self, stirrer_num):
        self.device_handler.stirrer_on(stirrer_num)
    
    def stirrer_off(self, stirrer_num):
        self.device_handler.stirrer_off(stirrer_num)


    def circulation_pump_on(self):
        self.device_handler.circulation_pump_on()
    
    def circulation_pump_off(self):
        self.device_handler.circulation_pump_off()
