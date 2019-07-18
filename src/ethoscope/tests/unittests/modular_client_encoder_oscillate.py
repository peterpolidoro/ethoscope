from modular_client import ModularClients
import time
import numpy as np
import matplotlib.pyplot as plt

devs = ModularClients()  # Might automatically find device if one available

channel = 0
velocity = 720
duration = 400
acceleration = 10000
deceleration = 10000
count = 4

stepper_controller = devs['ethoscope_stepper_controller']['5x3'][0]
encoder_interface = devs['encoder_interface_magnetic']['5x3'][0]

degrees_per_revolution = 360
positions_per_revolution = encoder_interface.get_positions_per_revolution()
milliseconds_per_second = 1000
encoder_interface.sample_period('setValue',10)
sample_period = encoder_interface.sample_period()
position_max = velocity*duration/milliseconds_per_second

stepper_controller.wake_all()
encoder_interface.set_time(time.time())
while True:
    encoder_interface.clear_samples()
    encoder_interface.set_position(0)
    encoder_interface.start_sampling()
    stepper_controller.oscillate(channel,velocity,duration,acceleration,deceleration,count)
    time.sleep(duration*count*2.1/milliseconds_per_second)
    encoder_interface.stop_sampling()
    samples = encoder_interface.get_samples()
    samples = np.array(samples)
    t = samples[:,1] - samples[0,1]
    p = samples[:,2]
    p = (p * degrees_per_revolution) / positions_per_revolution
    plt.plot(t,p,label='noisy position')
    plt.xlabel('time (ms)')
    plt.ylabel('position (degrees)')
    plt.title('velocity={0}, duration={1}, acceleration={2}, deceleration={3}'.format(velocity,duration,acceleration,deceleration))
    plt.xlim(0,duration*count*2.1)
    plt.ylim(0,position_max)
    plt.show()
stepper_controller.stop_all()
stepper_controller.sleep_all()
encoder_interface.stop_sampling()
encoder_interface.clear_samples()
