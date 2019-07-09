from modular_client import ModularClients
from collections import defaultdict
import time
import ast
import csv
import time

# Test modular client 
devs = ModularClients()  # Might automatically find device if one available
#print(devs.items())
#all_v = defaultdict(list)

try: 
    if devs is not None:
        dev0 = devs['ethoscope_stepper_controller']['5x3'][0]
        dev1 = devs['ethoscope_stepper_controller']['5x3'][1]
        dev0.wake_all()
        dev1.wake_all()
        #acc= 50
        #dev0.acceleration_max('setAllElementValues', str(acc))
        #dev1.acceleration_max('setAllElementValues', '50')
        #dev0.velocity_max('setAllElementValues', '1500')
        #dev0.velocity_min('setAllElementValues', '-1500')
        #dev1.velocity_max('setAllElementValues', '1500')
        #dev1.velocity_min('setAllElementValues', '-1500')
        #dev0.move_at_for(2, 180, 10000)
        #speed = 90
        #acc = 500
        dev0.move_at_for(0, 180, 5000, 10000, 10000)
        time.sleep(1)
finally:

    if devs is not None:
        dev0.stop_all()
        dev1.stop_all()
        dev0.sleep_all()
        dev1.sleep_all()
        

