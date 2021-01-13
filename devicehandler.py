



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
        self.id = str(machine.unique_id())
        self.configs = configs[self.id]
        # This is a dictionary of all the available pins, allowing pins to be accessed with self.pins["pump"]
        self.pins = self.configure_pins()
        # Initializes the I2C machine
        self.i2c = self.configure_i2c()


    def configure_i2c(self):
        i2c = machine.I2C(-1, machine.Pin(self.configs["i2c"]["I2C_clock"]), machine.Pin(self.configs["i2c"]["I2C_data"]))
        print(i2c)
        print(i2c.scan())
        return i2c

    def configure_pins(self):
        pin_dict = {}
        for pin in self.configs["pin"]:
            if pin != "pressure_sensor" and pin != "DS18B20_reservoir" and pin != "DS18B20_lower":
                print(pin)
                pin_dict[pin] = machine.Pin(self.configs["pin"][pin], machine.Pin.OUT)
            else:
                pin_dict[pin] = machine.Pin(self.configs["pin"][pin])
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
        self.pins["light_upper_outer"].on()
        self.pins["light_upper_inner"].on()
        self.pins["light_lower_outer"].on()
        self.pins["light_lower_inner"].on()
        self.pins["solenoid_lower_left"].off()
        self.pins["solenoid_lower_right"].off()
        self.pins["solenoid_upper_left"].off()
        self.pins["solenoid_upper_right"].off()
        self.pins["main_pump"].on()

    def read_pressure(self):
        adc = machine.ADC(self.pins["pressure_sensor"])
        adc.atten(machine.ADC.ATTN_11DB)
        adc.width(machine.ADC.WIDTH_12BIT)

        #Caclulate pressure
        pressure = 0
        voltagem = 0
        for i in range(100):
            adc_value = adc.read()
            voltage = 3.3 * (adc_value / 4095)
            voltagem += voltage
            pressure = pressure + 42 * voltage

        print(voltagem / i)
        self.logger.log("Pressure: " + str(pressure/i))

        return pressure / i

    def read_ds18b20(self, pin):
        sensor = ds18x20.DS18X20(onewire.OneWire(self.pins[pin]))
        try:
            roms = sensor.scan()
            sensor.convert_temp()
            sleep_ms(750)
            temps = []
            # measure the right then the left sensors
            for rom in roms:
                temp = sensor.read_temp(rom)
                temps.append(temp)
        except OSError as e:
            self.logger.log("Failed to read DS18B20 sensor")
            temp = 0
        return temps

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

        self.open_solenoids()

        sleep(10)
        self.logger.log("Closing solenoids")

        self.close_solenoids()

    def read_all_data(self):
        data = {}
        data["time_sent"] = str(machine.RTC().datetime())
        if self.configs["esp_type"]["pressure_reader"]:
            data["pressure"] = self.read_pressure()
        if self.configs["esp_type"]["pH_reader"]:
            data["pH"] = self.read_ph()
        if self.configs["esp_type"]["ec_reader"]:
            data["ec"] = self.reac_ec()
        if self.configs["esp_type"]["temp_reader"]:
            data["temperature_reservoir"] = self.read_ds18b20(self.pins["DS18B20_reservoir"])

        return data


    def check_phase(self, shelf):

        # Get current time
        current_time = machine.RTC().datetime()

        if shelf == "lower":
            shelf_phase = self.configs["date"]["lower_grow_start_date"]

        if shelf == "upper":
            shelf_phase = self.configs["date"]["upper_grow_start_date"]
            
        cleaned = shelf_phase.split(",")
        time_list = []
        for num in cleaned:
            time_list.append(int(num))

        sec_elapsed = mktime(current_time) - mktime(time_list)
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
      
    def check_pump(self):
        if self.read_pressure() < 80: 
            while self.read_pressure() < 100:
                 self.turn_on_pump()
            self.turn_off_pump()
            
    def check_fans(self):
        for pin in self.pins:
            if "plant" in pin and "DHT" not in pin:
                temperatures = self.read_ds18b20(pin)
                measured_temperature = sum(temperatures) / len(temperatures)
                if measured_temperature > self.configs["fan_trigger_temperature"]:
                    if "lower " in pin:
                        self.pins["fan_lower"].on()
                    if "upper" in pin: 
                        self.pins["fan_upper"].on()
                else:
                    if "lower " in pin:
                        self.pins["fan_lower"].off()
                    if "upper" in pin: 
                        self.pins["fan_upper"].off()
                        
    def test_pump(self):
        self.pins["main_pump"].on()
        sleep(10)
        self.pins["main_pump"].off()
      
    def test_solenoids(self):
        self.open_close_solenoids()
      
    def turn_off_pump(self):
        self.pins["main_pump"].on()
    
    def turn_on_pump(self):
        self.pins["main_pump"].off()
        
    def open_solenoids(self):
        self.pins["solenoid_upper_left"].on()
        self.pins["solenoid_upper_right"].on()
        self.pins["solenoid_lower_left"].on()
        self.pins["solenoid_lower_right"].on()
    
    def close_solenoids(self):
        self.pins["solenoid_upper_left"].off()
        self.pins["solenoid_upper_right"].off()
        self.pins["solenoid_lower_left"].off()
        self.pins["solenoid_lower_right"].off()
        
    def lights_on(self):
        self.pins["light_upper_outer"].off()
        self.pins["light_upper_inner"].off()
        self.pins["light_lower_outer"].off()
        self.pins["light_lower_inner"].off()
    
    def lights_off(self):    
        self.pins["light_upper_outer"].on()
        self.pins["light_upper_inner"].on()
        self.pins["light_lower_outer"].on()
        self.pins["light_lower_inner"].on()
        
    
    def upper_outer_on(self):
        self.pins["light_upper_outer"].on()
    
    def upper_outer_off(self):
        self.pins["light_upper_outer"].off()
        
    def upper_inner_on(self):
        self.pins["light_upper_inner"].on()
    
    def upper_inner_off(self):
        self.pins["light_upper_inner"].off()
        
    def lower_outer_on(self):
        self.pins["light_lower_outer"].on()
    
    def lower_outer_off(self):
        self.pins["light_lower_outer"].off()
        
    def lower_inner_on(self):
        self.pins["light_lower_inner"].on()
    
    def lower_inner_off(self):
        self.pins["light_lower_inner"].off()   
        
    
    
    def s_upper_left_on(self):
        self.pins["solenoid_upper_left"].on()
    
    def s_upper_left_off(self):
        self.pins["solenoid_upper_left"].off()
        
    def s_upper_right_on(self):
        self.pins["solenoid_upper_right"].on()
    
    def s_upper_right_off(self):
        self.pins["solenoid_upper_right"].off()
        
    def s_lower_left_on(self):
        self.pins["solenoid_lower_left"].on()
    
    def s_lower_left_off(self):
        self.pins["solenoid_lower_left"].off()
        
    def s_lower_right_on(self):
        self.pins["solenoid_lower_right"].on()
    
    def s_lower_right_off(self):
        self.pins["solenoid_lower_right"].off()   

    
    
    def p_pump_on(self):
        p_pump = []
        if "p_pump" in self.configs[pin].key:
            p_pump.append(self.configs[pin])
        for pump in p_pump:
            pump.on()
            sleep(10)
            pump.off()
    
    
    def fan_upper_on(self):
        self.pins["fan_upper"].on()
    
    def fan_upper_off(self):
        self.pins["fan_upper"].off()
    
    def fan_lower_on(self):
        self.pins["fan_lower"].on()
    
    def fan_lower_off(self):
        self.pins["fan_lower"].off()
    
    
    


















