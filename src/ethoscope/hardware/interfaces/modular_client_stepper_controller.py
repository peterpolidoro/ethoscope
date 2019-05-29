__author__ = 'elmalakis'

import logging
import time
from ethoscope.hardware.interfaces.interfaces import BaseInterface
from modular_client import ModularClients

class ModularClientInterface(BaseInterface):
    _dev0 = None
    _dev1 = None

    def __init__(self, port0=None, port1=None, *args, **kwargs):
        """
        Class to connect and abstract the Modular Client stepper controller.

        :param port1: the serial port to use for first motion controller board. Automatic detection if ``None``.
        :param port1: the serial port to use for second motion controller board. Automatic detection if ``None``.
        :param args: additional arguments
        :param kwargs: additional keyword arguments
        """

        print('Connecting to stepper controller ... ')

        if port0 is None and port1 is None:
            self._dev0, self._dev1 = self._find_ports()
        else:
            self._dev0 = port0
            self._dev1 = port1
            
        # wake up all motors        
        self._wake_all()
        self._warm_up()
        # reset the positions of the motors
        self._reset_all()

        super(ModularClientInterface, self).__init__(*args, **kwargs)

    def _find_ports(self):
        devs = ModularClients()  # Might automatically find device if one available
        print(devs.items())
        # TODO: check first that the driver is available before accessing it in the dictionary
        dev0 = devs['ethoscope_stepper_controller']['5x3'][0]
        dev1 = devs['ethoscope_stepper_controller']['5x3'][1]

        return dev0, dev1

    def _reset_all(self):
        if self._dev0 is not None and self._dev1 is not None:
            self._dev0.stop_all()
            self._dev0.zero_all()
            self._dev0.acceleration_max('setAllElementValues', '10000')  # fix the acceleration of all the motors at 1000
            self._dev0.velocity_max('setAllElementValues', '720')
            self._dev0.velocity_min('setAllElementValues', '-720')
            
            self._dev1.stop_all()
            self._dev1.zero_all()
            self._dev1.acceleration_max('setAllElementValues', '10000')  # fix the acceleration of all the motors at 1000
            self._dev1.velocity_max('setAllElementValues', '720')
            self._dev1.velocity_min('setAllElementValues', '-720')
            
        else:
            raise Exception("Could not initialize the motor boards.")
     
    def _wake_all(self):
        if self._dev0 is not None and self._dev1 is not None:
            self._dev0.wake_all()
            self._dev1.wake_all()
        else:
            raise Exception("Could not wake up the motor boards.")
    

    def move_with_speed(self, board, channel, speed=180, acceleration=100, deceleration=100, duration=5000):
        """
        Move a specified rotation to a speed for a certain time.

        :param board: the board number (0 or 1)
        :type channel: int
        :param channel: the number of the stepper motor to be moved
        :type channel: int
        :param speed: the speed, between -360 and 360 (degree/s). The sign indicates the rotation direction (CW or CCW)
        :type speed: int
        :param acceleration: the acceleration, between 100 and 10000 (degree/s^2).
        :type acceleration: int
        :param deceleration the deceleration, between 100 and 10000 (degree/s^2).
        :type deceleration: int
        :param duration: the time (ms) the stimulus should last
        :type duration: int
        :return:
        """

        if channel < 0 or channel > 6:
            raise Exception("idx channel must be between 0 and 6")

        if board < 0 or board > 1:
            raise Exception("idx board must be 0 or 1")


        motor = None

        if board == 0:
            motor = self._dev0
        elif board == 1:
            motor = self._dev1

        if motor is not None:
            motor.move_at_for(channel, speed, duration, acceleration, deceleration)

        else:
            raise Exception("Motors are not configured to apply stimulus")

        return
    

    def shake_with_speed(self, board, channel, speed=180, acceleration=100000, deceleration=100000, duration=5000):
        """
        Move a specified rotation to a speed for a certain time.

        :param board: the board number (0 or 1)
        :type channel: int
        :param channel: the number of the stepper motor to be moved
        :type channel: int
        :param speed: the speed, between -360 and 360 (degree/s). The sign indicates the rotation direction (CW or CCW)
        :type speed: int
        :param acceleration: the acceleration, between 100 and 10000 (degree/s^2).
        :type acceleration: int
        :param deceleration the deceleration, between 100 and 10000 (degree/s^2).
        :type deceleration: int
        :param duration: the time (ms) the stimulus should last
        :type duration: int
        :return:
        """

        if channel < 0 or channel > 6:
            raise Exception("idx channel must be between 0 and 6")

        if board < 0 or board > 1:
            raise Exception("idx board must be 0 or 1")


        motor = None

        if board == 0:
            motor = self._dev0
        elif board == 1:
            motor = self._dev1

        if motor is not None:
            for i in range(5):
                # Change the rotation direction every iteration
                if i%2 == 0: direction_speed = speed
                else: direction_speed = -1 * speed

                motor.move_at_for(channel, direction_speed, duration/5, acceleration, deceleration)
                time.sleep(2)

        else:
            raise Exception("Motors are not configured to apply stimulus")

        return



    def sleep_all(self):
        if self._dev0 is not None and self._dev1 is not None:
            self._dev0.sleep_all()
            self._dev1.sleep_all()
        else:
            raise Exception("Could not sleep the motor boards.")


    def send(self, *args, **kwargs):
        """
        The default sending paradigm is empty
        """
        # raise NotImplementedError
        pass


    def _warm_up(self):
        """
        This will move all motors.
        Useful for testing
        """
        # for i in range(1, 1 + self._n_channels):
        #    self.send(i)
        self._dev0.move_all_at(180)
        self._dev1.move_all_at(180)
        time.sleep(10)
        self._dev0.stop_all()
        self._dev1.stop_all()
        self._dev0.zero_all()
        self._dev1.zero_all()



