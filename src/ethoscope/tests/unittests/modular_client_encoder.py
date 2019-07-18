from modular_client import ModularClients
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splrep, splev

devs = ModularClients()  # Might automatically find device if one available

channel = 0
velocity = 720
duration = 10000
acceleration = 10000
deceleration = 10000

stepper_controller = devs['ethoscope_stepper_controller']['5x3'][0]
encoder_interface = devs['encoder_interface_magnetic']['5x3'][0]

degrees_per_revolution = 360
positions_per_revolution = encoder_interface.get_positions_per_revolution()
milliseconds_per_second = 1000
sample_period = encoder_interface.sample_period()
spline_k = 5
spline_smoothing = 100
velocity_max = 800

stepper_controller.wake_all()
encoder_interface.set_time(time.time())
encoder_interface.clear_samples()
encoder_interface.set_position(0)
encoder_interface.start_sampling()
stepper_controller.move_at_for(channel,velocity,duration,acceleration,deceleration)
time.sleep(10)
encoder_interface.stop_sampling()
samples = encoder_interface.get_samples()
samples = np.array(samples)
t = samples[:,1] - samples[0,1]
p = samples[:,2]
p = (p * degrees_per_revolution) / positions_per_revolution
# plt.plot(t,p,label='noisy position')
f = splrep(t,p,k=spline_k,s=spline_smoothing)
# plt.plot(t,splev(t,f),label='fitted position')
v = splev(t,f,der=1) * milliseconds_per_second
plt.plot(t,v)
plt.xlabel('time (ms)')
plt.ylabel('velocity (degrees/s)')
plt.title('velocity={0}, duration={1}, acceleration={2}, deceleration={3}'.format(velocity,duration,acceleration,deceleration))
plt.xlim(0,duration)
plt.ylim(0,velocity_max)
plt.show()
stepper_controller.stop_all()
stepper_controller.sleep_all()
encoder_interface.stop_sampling()
encoder_interface.clear_samples()
