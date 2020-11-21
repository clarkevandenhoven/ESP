import BoardUtility, config
import os, ntptime
from machine import RTC
from time import sleep

#Establish wifi connection
BoardUtility.connect_wifi()

#Set RTC to UTC time
ntptime.settime()

#Set initial relay states
BoardUtility.set_initial_state()

#Begin loop
while True:

  while RTC().datetime()[5]%3 == 0:

    #Open solenoid
    print("Opening solenoids, Time: ", RTC().datetime())

    config.solenoid_lower_left.off()
    config.solenoid_lower_right.off()
    config.solenoid_upper_left.off()
    config.solenoid_upper_right.off()

    sleep(10)

    #Close solenoid
    print("Closing solenoids, Time: ", RTC().datetime())
    config.solenoid_lower_left.on()
    config.solenoid_lower_right.on()
    config.solenoid_upper_left.on()
    config.solenoid_upper_right.on()

    if RTC().datetime()[5]%15 == 0:
      #Get all data points and upload
      BoardUtility.upload_full_data()
    else:
      #Upload tank psi only
      BoardUtility.upload_psi_data()

    #Check tank pressure, and turn on pump if pressure below 80 psi
    if BoardUtility.read_pressure() < 80:

      #Turn on pump
      config.pump.off()
      print("pump on")

      while BoardUtility.read_pressure() < 100:
        sleep(1)

      #Turn off pump
      config.pump.on()
      print("pump off")

      BoardUtility.upload_psi_data()


    BoardUtility.check_lights("upper")
    BoardUtility.check_lights("lower")

    sleep(60)












