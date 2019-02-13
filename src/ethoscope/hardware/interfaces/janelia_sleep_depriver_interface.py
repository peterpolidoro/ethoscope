__author__ = 'elmalakis'

from ethoscope.hardware.interfaces.modular_client_stepper_controller import ModularClientInterface


class JaneliaSleepDepriverInterface(ModularClientInterface):
    def send(self, board=None, channel=None, speed=100):
        """
        Sleep deprive an animal by rotating its tube.

        :param board: the board number (0 or 1)
        :type channel: int
        :param channel: the number of the stepper motor to be moved
        :type channel: int
        :param speed: the speed, between -100 and 100. The sign indicates the rotation direction (CW or CCW)
        :type speed: int
        """

        self.move_with_speed(board, channel, speed)
