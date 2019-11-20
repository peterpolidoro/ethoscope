__author__ = 'elmalakis'

from ethoscope.hardware.interfaces.modular_client_stepper_controller import ModularClientInterface


class JaneliaAdaptiveSleepDepriverInterface(ModularClientInterface):
    def send(self, board=None, channel=None, speed=180, duration=5000, acc=100, dec=100, velocity=0.5):
        """
        Sleep deprive an animal by rotating its tube.

        :param board: the board number (0 or 1)
        :type channel: int
        :param channel: the number of the stepper motor to be moved
        :type channel: int
        :param speed: the speed, between -360 and 360 (degree/s) The sign indicates the rotation direction (CW or CCW)
        :type speed: int
        :param duration: the duration of time to rotate the tube in ms (max is 6s. The masking duration in ethomics is 6s)
        :type: duration: int
        :param acc: the acceleration, between 100 and 10000 (degree/sec^2)
        :type: acc: int
        :param dec: the deceleration, between 100 and 10000 (degree/sec^2)
        :type: dec: int
        :param velocity: fly velocity in m/s
        :type: duration: float
        """
        print("send: %d %d %d %d" %(speed, duration, acc, dec))
        self.move_with_speed(board,
                             channel,
                             speed=speed,
                             duration=duration,
                             acceleration=acc,
                             deceleration=dec)


class JaneliaShakerSleepDepriverInterface(ModularClientInterface):
    def send(self, board=None, channel=None, speed=180, duration=1000, acc=10000, dec=10000, velocity=0.5, ncycles=4):
        """
        Sleep deprive an animal by shaking its tube.

        :param board: the board number (0 or 1)
        :type channel: int
        :param channel: the number of the stepper motor to be moved
        :type channel: int
        :param speed: the speed, between -360 and 360 (degree/s) The sign indicates the rotation direction (CW or CCW)
        :type speed: int
        :param duration: the duration of time to rotate the tube in ms (max is 6s. The masking duration in rethomics tool is 6s)
        :type: duration: int
        :param acc: the acceleration, between 100 and 10000 (degree/sec^2)
        :type: acc: int
        :param dec: the deceleration, between 100 and 10000 (degree/sec^2)
        :type: dec: int
        :param velocity: fly velocity in m/s
        :type: duration: float
        :param ncycles: the number of oscillation
        :type: ncycles: int
        """
        print("send shaker: %d %d %d %d" % (speed, duration, acc, dec))
        self.shake_with_speed(board,
                              channel,
                              speed=speed,
                              duration=duration,
                              acceleration=acc,
                              deceleration=dec,
                              ncycles=ncycles)
