__author__ = 'elmalakis'

from ethoscope.hardware.interfaces.modular_client_stepper_controller import ModularClientInterface


class JaneliaAdaptiveSleepDepriverInterface(ModularClientInterface):
    def send(self, board=None, channel=None, speed=180, duration=5000, acceleration=100, deceleration=100, velocity=0.5):
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
        :param acceleration: the acceleration, between 100 and 10000 (degree/sec^2)
        :type: acceleration: int
        :param deceleration: the deceleration, between 100 and 10000 (degree/sec^2)
        :type: deceleration: int
        :param velocity: fly velocity in m/s
        :type: duration: float
        """
        print("send: %d %d %d %d" %(speed, duration, acceleration, deceleration))
        self.move_with_speed(board,
                             channel,
                             speed=speed,
                             duration=duration,
                             acceleration=acceleration,
                             deceleration=deceleration)


class JaneliaShakerSleepDepriverInterface(ModularClientInterface):
    def send(self, board=None, channel=None, speed=180, duration=5000, acceleration=2000, deceleration=2000, velocity=0.5):
        """
        Sleep deprive an animal by shaking its tube.

        :param board: the board number (0 or 1)
        :type channel: int
        :param channel: the number of the stepper motor to be moved
        :type channel: int
        :param speed: the speed, between -360 and 360 (degree/s) The sign indicates the rotation direction (CW or CCW)
        :type speed: int
        :param duration: the duration of time to rotate the tube in ms (max is 6s. The masking duration in ethomics is 6s)
        :type: duration: int
        :param acceleration: the acceleration, between 100 and 10000 (degree/sec^2)
        :type: acceleration: int
        :param deceleration: the deceleration, between 100 and 10000 (degree/sec^2)
        :type: deceleration: int
        :param velocity: fly velocity in m/s
        :type: duration: float
        """

        self.shake_with_speed(board,
                              channel,
                              speed=speed,
                              duration=duration,
                              acceleration=acceleration,
                              deceleration=deceleration)
