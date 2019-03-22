from modular_client import ModularClients
from collections import defaultdict
import time
import ast
import csv


# Test modular client 
devs = ModularClients()  # Might automatically find device if one available
#print(devs.items())
all_v = defaultdict(list)

try: 
    if devs is not None:
        dev0 = devs['ethoscope_stepper_controller']['5x3'][0]
        dev1 = devs['ethoscope_stepper_controller']['5x3'][1]
        dev0.wake_all()
        dev1.wake_all()
        dev0.acceleration_max('setAllElementValues', '1000')
        dev1.acceleration_max('setAllElementValues', '1000')
        dev0.velocity_max('setAllElementValues', '2520')
        dev0.velocity_min('setAllElementValues', '-2520')
        dev1.velocity_max('setAllElementValues', '2520')
        dev1.velocity_min('setAllElementValues', '-2520')
        #dev0.move_at_for(2, 180, 10000)
        speed = 90
        now = time.time()
        while True:
            dev0.move_all_at(speed)
            vel = dev0.get_velocities()
            if speed > 450:
                dev0.stop_all()
                break
           
            #special case for 450
            elif speed == 450 and all(v == 359 for v in vel):
                all_v[speed].append((time.time() - now, vel[0]))
                print(str(speed)+' '+ str(vel[0]))
                dev0.stop_all()
                break
            
            elif all(speed-1<= v <=speed for v in vel):
                all_v[speed].append((time.time() - now, vel[0]))
                print(str(speed)+' '+ str(vel[0]))
                dev0.stop_all()
                
                now2 = time.time()
                while True: # wait untill motors stop moving
                    if not all(v == 0 for v in dev0.get_velocities()):
                        all_v[speed].append((time.time() - now, dev0.get_velocities()[0]))
                        time.sleep(0.1)
                        continue
                    else:
                        break
                print(str(speed) + ': time taken to stop: '+str(time.time()-now2))

                speed += 90
                continue 
            else:
               all_v[speed].append((time.time()-now, vel[0]))
               print(str(speed)+' '+ str(vel[0]))
            time.sleep(0.1)


        print('---- Write time vs. speed dictionary----')
        for key in all_v.keys():
            with open('/tmp/speedinfo'+str(key)+'.csv', 'wb') as f:
                writer = csv.writer(f)
                #writer.writerows(['time', 'speed'])
                for row in all_v[key]:
                    writer.writerow(row)
                #for key, value in all_v.items():
                #    writer.writerow([key, value])
        #dev1.move_at_for()
        #dev0.move_all_at(90)
        #dev1.move_all_at(90)
        #time.sleep(60)
        #dev0.stop_all()
        #dev1.stop_all()
        #dev0.sleep_all()
        #dev1.sleep_all()
    else:
        raise Exception ('Could not put motor controllers to sleep')
finally:

    if devs is not None:
        dev0.stop_all()
        dev1.stop_all()
        dev0.sleep_all()
        dev1.sleep_all()
        
