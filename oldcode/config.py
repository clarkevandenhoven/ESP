from machine import Pin

"""Declare grow phase start/end dates"""
GROW_START_DATE_UPPER = (2020, 10, 10, 1, 00, 00, 00, 644415)
GROW_START_DATE_LOWER = (2020, 9, 22, 1, 00, 00, 00, 644415)
GROW_PHASE_LENGTHS = [5,30,20]
GROW_PHASE = ["GERM","VEG","BLOOM"]
GROW_PHASE_LIGHT_HRS = {
  'GERM' : 16,
  'VEG': 18,
  'BLOOM' : 12
}
LIGHT_TRIGGER_HOUR = 10

"""Declare relay pin assignments"""
PUMP_PUN = 2
LIGHT_UPPER_OUTER_PIN = 23
LIGHT_UPPER_INNER_PIN = 19
LIGHT_LOWER_OUTER_PIN = 18
LIGHT_LOWER_INNER_PIN = 5
SOLENOID_UPPER_LEFT_PIN = 4
SOLENOID_UPPER_RIGHT_PIN = 0
SOLENOID_LOWER_LEFT_PIN = 17
SOLENOID_LOWER_RIGHT_PIN = 16

"""Delare sensor pin assignments"""
#DS18B20_RESERVOIR_PIN = 0
DS18B20_RESERVOIR_PIN = 25
DS18B20_ROOT_LOWER_LEFT_PIN = 27
DS18B20_ROOT_LOWER_RIGHT_PIN = 26
DHT22_PLANT_LOWER_LEFT_PIN = 33
DHT22_PLANT_LOWER_RIGHT_PIN = 32
I2C_DATA_PIN = 21
I2C_CLOCK_PIN = 22


"""Configure output pins to control relays"""
light_upper_outer = Pin(LIGHT_UPPER_OUTER_PIN, Pin.OUT)
light_upper_inner = Pin(LIGHT_UPPER_INNER_PIN, Pin.OUT)
light_lower_outer = Pin(LIGHT_LOWER_OUTER_PIN, Pin.OUT)
light_lower_inner = Pin(LIGHT_LOWER_INNER_PIN, Pin.OUT)
solenoid_lower_left = Pin(SOLENOID_LOWER_LEFT_PIN, Pin.OUT)
solenoid_lower_right = Pin(SOLENOID_LOWER_RIGHT_PIN, Pin.OUT)
solenoid_upper_left = Pin(SOLENOID_UPPER_LEFT_PIN, Pin.OUT)
solenoid_upper_right = Pin(SOLENOID_UPPER_RIGHT_PIN, Pin.OUT)
pump = Pin(PUMP_PUN, Pin.OUT)





