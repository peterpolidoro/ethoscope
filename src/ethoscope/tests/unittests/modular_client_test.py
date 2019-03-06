from modular_client import ModularClients
import time

# Test modular client 
devs = ModularClients()  # Might automatically find device if one available
#print(devs.items())
try: 
    if devs is not None:
        dev0 = devs['ethoscope_stepper_controller']['5x3'][0]
        dev1 = devs['ethoscope_stepper_controller']['5x3'][1]
        dev0.wake_all()
        dev1.wake_all()
        
        dev0.move_at_for(2, 180, 10000)
        #dev0.move_all_at(180)
        time.sleep(10)
        dev0.stop_all()
        dev0.sleep_all()
        dev1.sleep_all()
    else:
        raise Exception ('Could not put motor controllers to sleep')
finally:
    if devs is not None:
        dev0.sleep_all()
        dev1.sleep_all()
