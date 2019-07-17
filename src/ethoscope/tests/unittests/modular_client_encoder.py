from modular_client import ModularClients
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

devs = ModularClients()  # Might automatically find device if one available

channel = 0
velocity = 180
duration = 10000
acceleration = 10000
deceleration = 10000

stepper_controller = devs['ethoscope_stepper_controller']['5x3'][0]
encoder_interface = devs['encoder_interface_magnetic']['5x3'][0]

degrees_per_revolution = 360
positions_per_revolution = encoder_interface.get_positions_per_revolution()
milliseconds_per_second = 1000
sample_period = encoder_interface.sample_period()

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
x = samples[:,1] - samples[0,1]
# y = np.gradient(samples[:,2])
y = samples[:,2]
spl = UnivariateSpline(x,y,k=1)
plt.plot(x,spl(x))
plt.show()
# spl.set_smoothing_factor(10)
y = (spl.derivative()(x) * degrees_per_revolution * milliseconds_per_second) / positions_per_revolution
plt.plot(x,y)
plt.xlabel('time (ms)')
plt.ylabel('velocity (degrees/s)')
plt.show()
stepper_controller.stop_all()
stepper_controller.sleep_all()
encoder_interface.stop_sampling()
encoder_interface.clear_samples()
