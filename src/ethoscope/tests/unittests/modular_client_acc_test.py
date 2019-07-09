from modular_client import ModularClients
from collections import defaultdict
import time
import ast
import csv
import time

# Test modular client
devs = ModularClients()  # Might automatically find device if one available
# print(devs.items())
# all_v = defaultdict(list)

try:
    if devs is not None:
        dev0 = devs['ethoscope_stepper_controller']['5x3'][0]
        dev1 = devs['ethoscope_stepper_controller']['5x3'][1]
        dev0.wake_all()
        dev1.wake_all()
        dev1.acceleration_max('setAllElementValues', '50')
        dev0.velocity_max('setAllElementValues', '1500')
        dev0.velocity_min('setAllElementValues', '-1500')
        dev1.velocity_max('setAllElementValues', '1500')
        dev1.velocity_min('setAllElementValues', '-1500')

        now = time.time()
        acc_list = [100, 200, 300, 400, 500, 1000]
        vel_list = [90, 180, 360, 540, 720]
        for a in acc_list:
            all_v = defaultdict(list)  # new dictionary for each acc
            dev0.acceleration_max('setAllElementValues', str(a))
            print(' ------- A:' + str(a) + '-------')
            for v in vel_list:
                # while True:
                print(' ------- V:' + str(v) + '-------')
                dev0.move_all_at(v)
                now = time.time()
                while True:
                    curr_vel = dev0.get_velocities()

                    if all(v - 3 <= i <= v for i in curr_vel):
                        all_v[v].append((time.time() - now, curr_vel[0]))
                        # all_v[speed].append((time.time() - now, vel))
                        # print('reach speed: ' +str(speed)+' '+ str(vel[0]))
                        dev0.stop_all()

                        now2 = time.time()
                        while True:  # wait untill motors stop moving
                            if not all(i == 0 for i in dev0.get_velocities()):
                                # all_v[speed].append((time.time() - now, dev0.get_velocities()[0]))
                                all_v[v].append((time.time() - now, dev0.get_velocities()[0]))
                                time.sleep(0.05)
                                continue
                            else:
                                break
                        print(str(v) + ': time taken to stop: ' + str(time.time() - now2))

                        # speed += 180
                        break
                    else:
                        all_v[v].append((time.time() - now, curr_vel[0]))
                        # all_v[speed].append((time.time()-now, vel, acc))
                        # svel = [str[i] for i in vel]
                        print(str(v) + ' ' + str(curr_vel[0]))
                        # print(str(speed)+ ' '+ svel )
                        time.sleep(0.05)

            print('---- Write time vs. speed dictionary----')
            for key in all_v.keys():
                with open('/tmp/speedinfo_v' + str(key) + '_a' + str(a) + '.csv', 'wb') as f:
                    writer = csv.writer(f)
                    # writer.writerows(['time', 'speed'])
                    for row in all_v[key]:
                        writer.writerow(row)

                # for key, value in all_v.items():
                #    writer.writerow([key, value])

        # One time test
        # dev1.move_at_for()
        # dev0.move_all_at(720)
        # dev1.move_all_at(90)
        # time.sleep(10)
        # dev0.stop_all()
        # dev1.stop_all()
        # dev0.sleep_all()
        # dev1.sleep_all()
    else:
        raise Exception('Could not put motor controllers to sleep')
finally:

    if devs is not None:
        dev0.stop_all()
        dev1.stop_all()
        dev0.sleep_all()
        dev1.sleep_all()

