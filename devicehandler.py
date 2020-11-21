# This class serves as an interface between the ESP and the sensors
import machine
from time import sleep, sleep_ms
from utime import mktime
import ds18x20
import onewire
import dht
from logger import Logger
class DeviceHandler:

    ESP_LOG_FILE = "esp_log.txt"

    def __init__(self, configs):
        self.logger = Logger(self.ESP_LOG_FILE)
        self.configs = configs
        # This is a dictionary of all the available pins, allowing pins to be accessed with self.pins["pump"]
        self.pins = self.configure_pins(configs)
        # Initializes the I2C machine
        self.i2c = self.configure_i2c(configs)

    def configure_i2c(self, configs):
        i2c = machine.I2C(-1, machine.Pin(configs["i2c"]["I2C_clock"]), machine.Pin(configs["i2c"]["I2C_data"]))
        return i2c

    def configure_pins(self, configs):
        pin_dict = {}
        for pin in configs["pin"]:
            if pin != "pressure_sensor" OR pin != "DS18B20_reservoir":
                pin_dict[pin] = machine.Pin(configs["pin"][pin], machine.Pin.OUT)
            else:
                machine.Pin(configs["pin"][pin])
        return pin_dict

    def read_ec(self):
        ec_address = self.configs["i2c"]["ec"]
        # Request read from EC board
        self.i2c.writeto(ec_address, 'R')
        # Wait for 1 second for a response
        sleep(1)
        data = self.i2c.readfrom(ec_address, 9).decode("utf-8")
        ec, ppm = data[1:].split(",")
        self.logger.log("EC: " + str(ec) + ", PPM: " + str(ppm))
        return ec, ppm

    def read_ph(self):
        ph_address = self.configs["i2c"]["ph"]
        self.i2c.writeto(ph_address, 'R')
        # Wait for 1 second for a response
        sleep(1)
        data = self.i2c.readfrom(ph_address, 6).decode("utf-8")

        ph = data[1:]
        self.logger.log("pH: " + str(ph))
        return ph


    def set_initial_state(self):
        self.pins["light_upper_outer"].off()
        self.pins["light_upper_inner"].off()
        self.pins["light_lower_outer"].off()
        self.pins["light_lower_inner"].off()
        self.pins["solenoid_lower_left"].on()
        self.pins["solenoid_lower_right"].on()
        self.pins["solenoid_upper_left"].on()
        self.pins["solenoid_upper_right"].on()
        self.pins["pump"].on()

    def read_pressure(self):
        adc = machine.ADC(self.pins["pressure_sensor"])
        adc.atten(machine.ADC.ATTN_11DB)
        adc.width(machine.ADC.WIDTH_12BIT)

        #Caclulate pressure
        pressure = 0
        for i in range(100):
            adc_value = adc.read()
            voltage = 3.3 * (adc_value / 4095)
            pressure = pressure + 57.17 * voltage - 14.29

        self.logger.log("Pressure: " + str(pressure/i))

        return pressure / i

    def read_ds18b20(self, pin):
        sensor = ds18x20.DS18X20(onewire.OneWire(self.pins[pin]))
        try:
            roms = sensor.scan()
            sensor.convert_temp()
            sleep_ms(750)
            for rom in roms:
                temp = sensor.read_temp(rom)
        except OSError as e:
            self.logger.log("Failed to read DS18B20 sensor")
            temp = 0
        return temp

    def read_dht22(self, pin):
        sensor = dht.DHT22(self.pins[pin])
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
        except OSError as e:
            self.logger.log("Failed to read DHT sensor")
            temp = 0
            hum = 0

        return temp, hum

    def open_close_solenoids(self):
        self.logger.log("Opening solenoids")

        self.pins["solenoid_upper_left"].off()
        self.pins["solenoid_upper_right"].off()
        self.pins["solenoid_lower_left"].off()
        self.pins["solenoid_lower_right"].off()

        sleep(10)
        self.logger.log("Closing solenoids")

        self.pins["solenoid_upper_left"].on()
        self.pins["solenoid_upper_right"].on()
        self.pins["solenoid_lower_left"].on()
        self.pins["solenoid_lower_right"].on()

    def read_all_data(self):
        data = {}
        data["time_sent"] = str(machine.RTC().datetime())
        data["pressure"] = self.read_pressure()
        data["pH"] = self.read_ph()
        data["ec"] = self.reac_ec()
        data["temperature_reservoir"] = self.read_ds18b20(self.pins["DS18B20_reservoir"])

        return data


    def check_phase(self, shelf):

        # Get current time
        current_time = machine.RTC().datetime()

        if shelf == "lower":
            shelf_phase = self.configs["date"]["lower_grow_start_date"]

        if shelf == "upper":
            shelf_phase == self.configs["date"]["upper_grow_start_date"]

        sec_elapsed = mktime(current_time) - mktime(shelf_phase)
        days_elapsed = sec_elapsed / (24 * 60 * 60)

        if days_elapsed <= self.configs["phase"]["germ"]["length_in_days"]:
            phase = "germ"
        elif days_elapsed <= self.configs["phase"]["veg"]["length_in_days"]:
            phase = "veg"
        else:
            phase = "bloom"

        return phase

    def turn_lights_on(self, grow_phase, shelf):

        if shelf == "upper":
            if grow_phase == "germ":
                self.pins["light_upper_inner"].on()
            elif grow_phase == "veg":
                self.pins["light_upper_outer"].on()
            else:
                self.pins["light_upper_inner"].on()
                self.pins["light_upper_outer"].on()
        else:
            if grow_phase == "germ":
                self.pins["light_lower_outer"].on()
            if grow_phase == "veg":
                self.pins["light_lower_inner"].on()
            else:
                self.pins["light_lower_outer"].on()
                self.pins["light_lower_inner"].on()

    def turn_lights_off(self, grow_phase, shelf):

        if shelf == "lower":
            self.pins["light_lower_inner"].off()
            self.pins["light_lower_outer"].off()

        if shelf == "upper":
            self.pins["light_upper_inner"].off()
            self.pins["light_upper_outer"].off()

    def check_lights(self):
        shelves = ["upper", "lower"]
        for shelf in shelves:
            phase = self.check_phase(shelf)

            light_off_duration = 24 - self.configs["phase"][phase]["light_hours"]

            current_time = machine.RTC().datetime()
            current_hour = current_time[4]

            if current_hour == self.configs["light_trigger_hour"]:
                self.logger.log("Turn " + shelf + " light off")
                self.turn_lights_off(phase, shelf)
            elif current_hour == (self.configs["light_trigger_hour"] + light_off_duration):
                self.logger.log("Turn " + shelf + " light on")
                self.turn_lights_on(phase, shelf)
     
    def test_pump(self):
        self.pins["pump"].on()
        sleep(10)
        self.pins["pump"].off()
      
    def test_solenoids(self):
        self.open_close_solenoids()
      
    def test_ec(self):
        ec, ppm = self.read_ec()
        print("EC: " + ec + " PPM: " + ppm)
      
    def test_ph(self):
        pH = self.read_ph()
        print("pH: " + pH)
      
    def test_pressure(self):
          pressure = self.read_pressure()
          print("Pressure: " + pressure)
    
    def test_ds18b20(self, pin_name):
          temp = self.read_ds18b20(self.pins["pin_name"])
          print("Temperature: " + temp)
          


