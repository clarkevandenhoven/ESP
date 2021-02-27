# Main file that gets executed
import os 
import machine
from time import sleep, time
from system import System


#for i in range(1):
  #s = System()
  #sleep(1)
  #s.turn_off_pump()
  #s.lights_off()
  #sleep(5)
  #s.run()

System().run()
#System().close_solenoids()
#System().open_solenoids()
#System().turn_on_pump()
#System().turn_off_pump()

#System().test_pressure()
#System().s_lower_left_on()
#System().s_lower_left_off()

#System().lights_off()

#System().upper_inner_on()
#System().lower_inner_on()
#System().test_pressure()

#System().test_ds18b20("DS18B20_root_upper")
#System().test_ds18b20("DS18B20_root_lower")

#System().test_ds18b20("DS18B20_plant_lower")
#System().test_ds18b20("DS18B20_plant_upper")
#System().test_ds18b20("DS18B20_plant_upper")


#System().fan_upper_on()
#System().fan_upper_off()

#System().fan_lower_on()
#System().fan_lower_off()

#print("hello")

#System().set_initial_state()


