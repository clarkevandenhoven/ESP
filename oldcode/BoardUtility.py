import config
import onewire, ds18x20, dht
import machine, time, network, urequests, ujson, ntptime, utime


# Connect board to wifi
def connect_wifi():
    ssid = "YOSHIDA"
    password =  "Brentwood11"

    station = network.WLAN(network.STA_IF)

    if station.isconnected() == True:
        print("Already connected")
        return

    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
        pass

    print("Connection successful")
    print(station.ifconfig())

# Function to get appropriate sensor data
def upload_full_data():

  payload = {}
  payload['time_sent'] = str(machine.RTC().datetime())
  payload['pressure'] = read_pressure()
  payload['pH'] = read_ph()
  payload['ec'], payload['ppm'] = read_ec()
  #payload['temperature_plant_lower_left'],payload['humidity_plant_lower_left'] = read_dht22(config.DHT22_PLANT_LOWER_LEFT_PIN)
  #payload['temperature_plant_lower_right'],payload['humidity_plant_lower_right'] = read_dht22(config.DHT22_PLANT_LOWER_RIGHT_PIN)
  #payload['temperature_root_lower_left'] = read_ds18b20(config.DS18B20_ROOT_LOWER_LEFT_PIN)
  #payload['temperature_root_lower_right'] = read_ds18b20(config.DS18B20_ROOT_LOWER_RIGHT_PIN)
  payload['temperature_reservoir'] = read_ds18b20(config.DS18B20_RESERVOIR_PIN)

  print(ujson.dumps(payload))

  response = urequests.put('https://team1-fydp.azurewebsites.net/result', headers = {'content-type': 'application/json'}, data = ujson.dumps(payload))
  print("Put server response = ",response.json())

  response = urequests.get('https://team1-fydp.azurewebsites.net/latest')
  print("Get server response = ",response.json())

def upload_temphum_data():

  payload = {}
  payload['time_sent'] = str(machine.RTC().datetime())

  payload['temperature_plant_lower_left'],payload['humidity_plant_lower_left'] = read_dht22(config.DHT22_PLANT_LOWER_LEFT_PIN)
  payload['temperature_plant_lower_right'],payload['humidity_plant_lower_right'] = read_dht22(config.DHT22_PLANT_LOWER_RIGHT_PIN)

  print(ujson.dumps(payload))

  response = urequests.put('https://team1-fydp.azurewebsites.net/result', headers = {'content-type': 'application/json'}, data = ujson.dumps(payload))
  print("Put server response = ",response.json())

  response = urequests.get('https://team1-fydp.azurewebsites.net/latest')
  print("Get server response = ",response.json())

def upload_psi_data():

  payload = {}
  payload['time_sent'] = str(machine.RTC().datetime())
  payload['pressure'] = read_pressure()

  print(ujson.dumps(payload))

  response = urequests.put('https://team1-fydp.azurewebsites.net/result', headers = {'content-type': 'application/json'}, data = ujson.dumps(payload))
  print("Put server response = ",response.json())

  response = urequests.get('https://team1-fydp.azurewebsites.net/latest')
  print("Get server response = ",response.json())



def upload_dht22_data():

  payload = {}
  payload['time_sent'] = str(machine.RTC().datetime())
  payload['temperature_plant_lower_left'],payload['humidity_plant_lower_left'] = read_dht22(config.DHT22_PLANT_LOWER_LEFT_PIN)
  payload['temperature_plant_lower_right'],payload['humidity_plant_lower_right'] = read_dht22(config.DHT22_PLANT_LOWER_RIGHT_PIN)

  print(ujson.dumps(payload))

  response = urequests.put('https://team1-fydp.azurewebsites.net/result', headers = {'content-type': 'application/json'}, data = ujson.dumps(payload))
  print("Put server response = ",response.json())

  response = urequests.get('https://team1-fydp.azurewebsites.net/latest')
  print("Get server response = ",response.json())

def read_ds18b20(pin):
  sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(pin)))
  print(sensor)
  try:
    roms = sensor.scan()
    print(roms)
    sensor.convert_temp()
    time.sleep_ms(750) # time needed to convert temperature
    for rom in roms:
      temp = sensor.read_temp(rom)
  except OSError as e:
    print('Failed to read DS18B20 sensor.')
    temp = 0

  return temp


def read_dht22(pin):
  

  sensor = dht.DHT22(machine.Pin(pin))
  try:
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
  except OSError as e:
    print('Failed to read DHT sensor.')
    temp = 0
    hum = 0

  return temp, hum

def read_ec():

  # Initialize i2c bus
  i2c = machine.I2C(-1, machine.Pin(22), machine.Pin(21))

  # hardcoded i2c address for the EZO EC board
  ec_i2c_address = 100

  #request read from EC board, wait 1 second to collect measurement
  i2c.writeto(ec_i2c_address,'R')
  time.sleep(1)
  data = i2c.readfrom(ec_i2c_address, 9)

  split = data.decode("utf-8")
  ec, ppm = split[1:].split(",")

  return ec, ppm

def read_ph():

  # Initialize i2c bus
  i2c = machine.I2C(-1, machine.Pin(22), machine.Pin(21))

  # hardcoded i2c address for the EZO PH board
  ph_i2c_address = 99

  #request read from pH board, wait 1 second to collect measurement
  i2c.writeto(ph_i2c_address,'R')
  time.sleep(1)
  data = i2c.readfrom(ph_i2c_address, 6)

  print(data)

  ph = data.decode("utf-8")[1:]

  return ph

def read_pressure():

  pressure_sensor_pin = 39

  # Define the adc pin
  adc = machine.ADC(machine.Pin(pressure_sensor_pin))
  adc.atten(machine.ADC.ATTN_11DB)
  adc.width(machine.ADC.WIDTH_12BIT)

  # Calculate pressure

  pressure = 0
  for i in range(100):
    adc_value = adc.read()
    voltage = 3.3*(adc_value/4095)
    pressure = pressure + 57.14*voltage - 14.29

  print(pressure/i)

  return pressure/i

def set_time():
  ntptime.settime()
  rtc = machine.RTC()
  utc_shift = -4*3600

  tm = utime.localtime(utime.mktime(utime.localtime()) + utc_shift)
  tm = tm[0:3] + (0,) + tm[3:6] + (0,)
  machine.RTC().init(tm)
  return

def set_initial_state():
  config.light_upper_outer.off()
  config.light_upper_inner.off()
  config.light_lower_outer.off()
  config.light_lower_inner.off()
  config.solenoid_lower_left.on()
  config.solenoid_lower_right.on()
  config.solenoid_upper_left.on()
  config.solenoid_upper_right.on()
  config.pump.on()
  return

def check_phase(shelf):

  #Get current time
  current_time = machine.RTC().datetime()

  if shelf == "lower":
    shelf_phase = config.GROW_START_DATE_LOWER

  if shelf == "upper":
    shelf_phase = config.GROW_START_DATE_UPPER

  #Calculate seconds elapsed since grow start time and convert to days
  seconds_elapsed = utime.mktime(current_time) - utime.mktime(shelf_phase)
  days_elapsed = seconds_elapsed/86400

  #Using days elapsed determine the current grow phase
  phase = "n/a"
  if days_elapsed <= config.GROW_PHASE_LENGTHS[0]:
    phase = "GERM"
  elif days_elapsed <= (config.GROW_PHASE_LENGTHS[0] + config.GROW_PHASE_LENGTHS[1]):
    phase = "VEG"
  else:
    phase = "BLOOM"

  return phase

def check_light_relay_status(grow_phase, shelf):

  #Check inner relays for GERM
  if shelf == "lower":
    if grow_phase == "GERM":
      return not config.light_lower_inner.value()

    #Check outer relays for VEG
    elif grow_phase == "VEG":
      return not config.light_lower_outer.value()

    #Check inner and outer relays for BLOOM
    elif grow_phase == "BLOOM":
      return not config.light_lower_inner.value() or not config.light_lower_outer.value()

  if shelf == "upper":
    if grow_phase == "GERM":
      return not config.light_upper_inner.value()

    #Check outer relays for VEG
    elif grow_phase == "VEG":
      return not config.light_upper_outer.value()

    #Check inner and outer relays for BLOOM
    elif grow_phase == "BLOOM":
      return not config.light_upper_inner.value() or not config.light_upper_outer.value()

def turn_lights_on(grow_phase, shelf):

  if shelf == "upper":
    #Check inner relays for GERM
    if grow_phase == "GERM":
      config.light_upper_inner.on()

    #Check outer relays for VEG
    elif grow_phase == "VEG":
      config.light_upper_outer.on()

    #Check inner and outer relays for BLOOM
    elif grow_phase == "BLOOM":
      config.light_upper_inner.on()
      config.light_upper_outer.on()

  if shelf == "lower":
    #Check inner relays for GERM
    if grow_phase == "GERM":
      config.light_lower_inner.on()

    #Check outer relays for VEG
    elif grow_phase == "VEG":
      config.light_lower_outer.on()

    #Check inner and outer relays for BLOOM
    elif grow_phase == "BLOOM":
      config.light_lower_inner.on()
      config.light_lower_outer.on()

def turn_lights_off(grow_phase, shelf):

  if shelf == "lower":
    config.light_lower_inner.off()
    config.light_lower_outer.off()

  if shelf == "upper":
    config.light_upper_inner.off()
    config.light_upper_outer.off()


def check_lights(shelf):
  #Get current grow phase
  phase = check_phase(shelf)

  #Calculate the light off duration
  light_on_duration = config.GROW_PHASE_LIGHT_HRS[phase]
  light_off_duration = 24 - light_on_duration

  #Get current hour from RTC time in UTC timezone
  current_time = machine.RTC().datetime()
  current_hour = current_time[4]

  #Get current relay status, returns 1 if a relay is currently on
  light_relay_status = check_light_relay_status(phase, shelf)

  """ Standard Operation Loop """
  #If current hour is 10am UTC (6am EST)
  if current_hour == config.LIGHT_TRIGGER_HOUR:
    #turn light off
    print('turn light off')
    turn_lights_off(phase, shelf)
  elif current_hour == (config.LIGHT_TRIGGER_HOUR + light_off_duration):
    #turn light on
    print('turn light on 1')
    turn_lights_on(phase, shelf)

  """ Outside of Normal Operation Loop
  This will turn on lights if the board is flashed during the light on period,
  the set_initial_state() in the main.py will set relays to on.
  """
  if current_hour < config.LIGHT_TRIGGER_HOUR and light_relay_status:
    #turn light on
    print('turn light on 2')
    turn_lights_on(phase, shelf)
  elif current_hour > (config.LIGHT_TRIGGER_HOUR + light_off_duration) and light_relay_status:
    #turn light on
    print('turn light on 3')
    turn_lights_on(phase, shelf)

















