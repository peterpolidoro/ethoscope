'''
any new class added here need to be added to web_utils/control_thread.py too
'''

__author__ = 'quentin'
# Modified by Salma Elmalaki for Janelia Ethoscope

from ethoscope.stimulators.stimulators import BaseStimulator, DoubleBaseStimulator, HasInteractedVariable

from ethoscope.hardware.interfaces.interfaces import  DefaultInterface
from ethoscope.hardware.interfaces.sleep_depriver_interface import SleepDepriverInterface, SleepDepriverInterfaceCR
from ethoscope.hardware.interfaces.janelia_sleep_depriver_interface import JaneliaAdaptiveSleepDepriverInterface, JaneliaShakerSleepDepriverInterface
from ethoscope.hardware.interfaces.optomotor import OptoMotor

from ethoscope.web_utils.helpers import get_machine_info

import time
import socket
import random
import logging
import datetime
import numpy as np
from math import log10



class IsMovingStimulator(BaseStimulator):
    _HardwareInterfaceClass = DefaultInterface

    def __init__(self, hardware_connection=None, velocity_threshold=0.0060, date_range = "", **kwargs):
        """
        class implementing an stimulator that decides whether an animal has moved though does nothing accordingly.
        :param hardware_connection: a default hardware interface object
        :param velocity_threshold: Up to which velocity an animal is considered to be immobile
        :type velocity_threshold: float
        """
        self._velocity_threshold = velocity_threshold
        self._last_active = 0
        self._current_velocity = 0.0    # Janelia: add velocity
        super(IsMovingStimulator, self).__init__(hardware_connection, date_range)

    def _has_moved(self):

        positions = self._tracker.positions

        if len(positions ) <2 :
            return False


        if len(positions[-1]) != 1:
            raise Exception("This stimulator can only work with a single animal per ROI")
        tail_m = positions[-1][0]

        times = self._tracker.times
        last_time_for_position = times[-1]
        last_time = self._tracker.last_time_point

        # we assume no movement if the animal was not spotted
        if last_time != last_time_for_position:
            return False

        dt_s = abs(times[-1] - times[-2]) / 1000.0
        dist = 10.0 ** (tail_m["xy_dist_log10x1000"]/1000.0)
        velocity = dist / dt_s

        self._current_velocity = velocity # Janelia: Update the velocity

        if velocity > self._velocity_threshold:
            return True
        return False

    def _get_velocity(self):
        return self._current_velocity

    def _decide(self):

        has_moved = self._has_moved()

        t = self._tracker.times
        if  has_moved:# or xor_diff > self._xor_speed_threshold :
            self._last_active = t[-1]
            return HasInteractedVariable(False), {}
        return HasInteractedVariable(True), {}


class IsMovingStimulatorDouble(DoubleBaseStimulator):
    _HardwareInterfaceClass = DefaultInterface

    def __init__(self, hardware_connection=None, velocity_threshold=0.0060, date_range = "", date_range2="", **kwargs):
        """
        class implementing a stimulator that decides whether an animal has moved though does nothing accordingly an communicate an operating signal to a second stimulus
        :param hardware_connection: a default hardware interface object
        :param velocity_threshold: Up to which velocity an animal is considered to be immobile
        :type velocity_threshold: float
        :param date_range: the start and stop date/time for the stimulator. Format described `here <https://github.com/gilestrolab/ethoscope/blob/master/user_manual/schedulers.md>`_
        :type date_range: str
        :param date_range2: the start and stop date/time for the second stimulator. Format described `here <https://github.com/gilestrolab/ethoscope/blob/master/user_manual/schedulers.md>`_
        :type date_range: str
        """
        self._velocity_threshold = velocity_threshold
        self._last_active = 0
        self._current_velocity = 0.0    # Janelia: add velocity
        super(IsMovingStimulatorDouble, self).__init__(hardware_connection, date_range, date_range2)

    def _has_moved(self):

        positions = self._tracker.positions

        if len(positions ) <2 :
            return False


        if len(positions[-1]) != 1:
            raise Exception("This stimulator can only work with a single animal per ROI")
        tail_m = positions[-1][0]

        times = self._tracker.times
        last_time_for_position = times[-1]
        last_time = self._tracker.last_time_point

        # we assume no movement if the animal was not spotted
        if last_time != last_time_for_position:
            return False

        dt_s = abs(times[-1] - times[-2]) / 1000.0
        dist = 10.0 ** (tail_m["xy_dist_log10x1000"]/1000.0)
        velocity = dist / dt_s

        self._current_velocity = velocity # Janelia: Update the velocity

        if velocity > self._velocity_threshold:
            return True
        return False

    def _get_velocity(self):
        return self._current_velocity

    def _decide(self):

        has_moved = self._has_moved()

        t = self._tracker.times
        if  has_moved:# or xor_diff > self._xor_speed_threshold :
            self._last_active = t[-1]
            return HasInteractedVariable(False), {}
        return HasInteractedVariable(True), {}

    def _communicate(self, communicate_signal):
        """
        communicate an operating signal to an outside stimulator

        :param communicate_signal: an ON and OFF signal to the external stimulator
        :type communicate_signal: bool
        """
        raise NotImplementedError

class SleepDepStimulator(IsMovingStimulator):
    _description = {"overview": "A stimulator to sleep deprive an animal using servo motor. See http://todo/fixme.html",
                    "arguments": [
                                    {"type": "number", "min": 0.0, "max": 1.0, "step":0.0001, "name": "velocity_threshold", "description": "The minimal velocity that counts as movement","default":0.0060},
                                    {"type": "number", "min": 1, "max": 3600*12, "step":1, "name": "min_inactive_time", "description": "The minimal time after which an inactive animal is awaken","default":120},
                                    {"type": "date_range", "name": "date_range",
                                     "description": "A date and time range in which the device will perform (see http://tinyurl.com/jv7k826)",
                                     "default": ""},
                                   ]}

    _HardwareInterfaceClass = SleepDepriverInterface
    _roi_to_channel = {
            1:1,  3:2,  5:3,  7:4,  9:5,
            12:6, 14:7, 16:8, 18:9, 20:10
        }

    def __init__(self,
                 hardware_connection,
                 velocity_threshold=0.0060,
                 min_inactive_time=120,  #s
                 date_range=""
                 ):
        """
        A stimulator to control a sleep depriver module.

        :param hardware_connection: the sleep depriver module hardware interface
        :type hardware_connection: :class:`~ethoscope.hardware.interfaces.sleep_depriver_interface.SleepDepriverInterface`
        :param velocity_threshold:
        :type velocity_threshold: float
        :param min_inactive_time: the minimal time without motion after which an animal should be disturbed (in seconds)
        :type min_inactive_time: float
        :return:
        """

        self._inactivity_time_threshold_ms = min_inactive_time *1000 #so we use ms internally
        self._t0 = None
        
        super(SleepDepStimulator, self).__init__(hardware_connection, velocity_threshold, date_range=date_range)



    def _decide(self):
        roi_id= self._tracker._roi.idx
        now =  self._tracker.last_time_point

        try:
            channel = self._roi_to_channel[roi_id]
        except KeyError:
            return HasInteractedVariable(False), {}

        has_moved = self._has_moved()

        if self._t0 is None:
            self._t0 = now

        if not has_moved:
            if float(now - self._t0) > self._inactivity_time_threshold_ms:
                self._t0 = None
                return HasInteractedVariable(True), {"channel":channel}
        else:
            self._t0 = now
        return HasInteractedVariable(False), {}


class SleepDepStimulatorCR(SleepDepStimulator):
    _description = {"overview": "A stimulator to sleep deprive an animal using servo motor in Continous Rotation mode. See http://todo/fixme.html",
                    "arguments": [
                                    {"type": "number", "min": 0.0, "max": 1.0, "step":0.0001, "name": "velocity_threshold", "description": "The minimal velocity that counts as movement","default":0.0060},
                                    {"type": "number", "min": 1, "max": 3600*12, "step":1, "name": "min_inactive_time", "description": "The minimal time after which an inactive animal is awaken","default":120},
                                    {"type": "date_range", "name": "date_range",
                                     "description": "A date and time range in which the device will perform (see http://tinyurl.com/jv7k826)",
                                     "default": ""}
                                   ]}

    _HardwareInterfaceClass = SleepDepriverInterfaceCR
    _roi_to_channel = {
            1:1,  3:2,  5:3,  7:4,  9:5,
            12:6, 14:7, 16:8, 18:9, 20:10
        }
    def __init__(self,
                 hardware_connection,
                 velocity_threshold=0.0060,
                 min_inactive_time=120,  #s
                 date_range=""
                 ):
        """
        A stimulator to control a sleep depriver module.

        :param hardware_connection: the sleep depriver module hardware interface
        :type hardware_connection: :class:`~ethoscope.hardware.interfaces.sleep_depriver_interface.SleepDepriverInterface`
        :param velocity_threshold:
        :type velocity_threshold: float
        :param min_inactive_time: the minimal time without motion after which an animal should be disturbed (in seconds)
        :type min_inactive_time: float
        :return:
        """

        self._inactivity_time_threshold_ms = min_inactive_time *1000 #so we use ms internally
        self._t0 = None
        
        super(SleepDepStimulator, self).__init__(hardware_connection, velocity_threshold, date_range=date_range)


class JaneliaAdaptiveSleepDepStimultor(IsMovingStimulator):

    _description = {"overview": "An adaptive stimulator to sleep deprive an animal using stepper motors.",
                    "arguments": [
                                    {"type": "number", "min": 0.0, "max": 1.0, "step":0.0001, "name": "velocity_threshold", "description": "The minimal velocity that counts as movement","default":0.0060},
                                    {"type": "number", "min": 1, "max": 3600*12, "step":1, "name": "min_inactive_time", "description": "The minimal time after which an inactive animal is awaken","default":120},
                                    {"type": "number", "min": 10, "max": 720 , "step": 1, "name": "min_motor_speed","description": "The motor speed in degree/sec", "default": 180},
                                    {"type": "number", "min": 10, "max": 720, "step": 1, "name": "delta_motor_speed", "description": "The increase/decrease in motor speed", "default": 90},
                                    {"type": "number", "min": 100, "max": 10000, "step": 1, "name": "min_motor_acceleration", "description": "The minimal motor acceleration", "default": 100},
                                    {"type": "number", "min": 100, "max": 10000, "step": 1, "name": "max_motor_acceleration", "description": "The maximal motor acceleration", "default": 10000},
                                    {"type": "number", "min": 10, "max": 10000, "step": 1, "name": "delta_motor_acceleration", "description": "The increase/decrease in motor acceleration", "default": 10},
                                    {"type": "number", "min": 10, "max": 10000, "step": 1, "name": "motor_deceleration", "description": "The motor deceleration", "default": 10000},
                                    {"type": "number", "min": 60, "max": 5*60, "step": 1, "name": "low_time_threshold", "description": "The minimal time threshold to increase the speed if fly falls asleep again quickly", "default": 120},
                                    {"type": "number", "min": 60, "max": 30*60, "step": 1, "name": "high_time_threshold", "description": "The maximal time threshold to decrease the speed if fly does not fall asleep quickly", "default": 60 * 30},
                                    {"type": "date_range", "name": "date_range",
                                     "description": "A date and time range in which the device will perform (see http://tinyurl.com/jv7k826)",
                                     "default": ""},
                                   ]}

    _HardwareInterfaceClass = JaneliaAdaptiveSleepDepriverInterface
    _roi_to_channel = {  # TODO: check if the roi and channel mapping are the same with the second rpi
        1: 6,
        2: 5,
        3: 4,
        4: 3,
        5: 2,
        6: 1,
        7: 0,
        8: 6,
        9: 5,
        10: 4,
        11: 3,
        12: 2,
        13: 1,
        14: 0
    }
    _roi_to_motor_board = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 1,
        13: 1,
        14: 1
    }
    
    # Linearly space the motor speed from 0 to 360 into 10000 steps to match the fly velocity
    #_motor_speed = [round(x) for x in np.linspace(0, 360, 10000+1)]

    # Create dictionary of current fly_velocity/motor_speed status for each roi
    _stimulus_info = {'t': 0, 'v': 0.006, 's': 90, 'a':100} # initialize the stimulus info for each roi
    _roi_stimulus_status = {1: _stimulus_info,
                                 2: _stimulus_info,
                                 3: _stimulus_info,
                                 4: _stimulus_info,
                                 5: _stimulus_info,
                                 6: _stimulus_info,
                                 7: _stimulus_info,
                                 8: _stimulus_info,
                                 9: _stimulus_info,
                                 10: _stimulus_info,
                                 11: _stimulus_info,
                                 12: _stimulus_info,
                                 13: _stimulus_info,
                                 14: _stimulus_info
                                 }

    # _time_delta_min = 1000 * 60 * 2       # 2 min for time delta (min time thresh in hysteresis)
    # _time_delta_max = 1000 * 60 * 30      # 30 min for time delta (max time thresh in hysteresis)
    #
    # _motor_speed_delta = 90      # 360 degree step for each increase/decrease in velocity
    # _min_motor_speed = 90
    # _max_motor_speed = 720      # based on modular_client max motor speed
    # _min_motor_acc = 100
    # _max_motor_acc = 10000
    #

    def __init__(self,
                 hardware_connection,
                 velocity_threshold= 0.0060,
                 min_inactive_time=120,
                 min_motor_speed=180,
                 delta_motor_speed=90,
                 min_motor_acceleration=100,
                 max_motor_acceleration=10000,
                 delta_motor_acceleration=10,
                 motor_deceleration=10000,
                 low_time_threshold=120,
                 high_time_threshold=1800,
                 date_range=""):
        """
        A stimulator to control a sleep depriver module.

        :param hardware_connection: the adaptive sleep depriver module hardware interface
        :type hardware_connection: :class:`~ethoscope.hardware.interfaces.janelia_sleep_depriver_interface.JaneliaAdaptiveSleepDepriverInterface`
        :param velocity_threshold:
        :type velocity_threshold: float
        :param min_inactive_time: the minimal time without motion after which an animal should be disturbed (in seconds)
        :type min_inactive_time: float
        :param min_motor_speed: the minimal motor speed in degree/sec
        :type min_motor_speed: int
        :param delta_motor_speed: the increase/decrease in motor speed
        :type delta_motor_speed: int
        :param min_motor_acceleration: the minimal motor acceleration in degree/sec^2
        :type min_motor_acceleration: int
        :param max_motor_acceleration: the maximal motor acceleration in degree/sec^2
        :type max_motor_acceleration: int
        :param delta_motor_acceleration: the increase/decrease in degree/sec^2
        :type delta_motor_acceleration: int
        :param motor_deceleration: the motor deceleration in degree/sec^2
        :type motor_deceleration: int
        :param low_time_threshold: the minimal time the fly falls back to sleep before increasing the speed and acceleration
        :type low_time_threshold: int
        :param high_time_threshold: the maximal time the fly falls back to sleep before decreasing the speed and acceleration
        :type high_time_threshold: int
        :return:
        """

        self._inactivity_time_threshold_ms = min_inactive_time * 1000  # so we use ms internally

        self._time_delta_min = low_time_threshold * 1000   # 2 min for time delta (min time thresh in hysteresis)
        self._time_delta_max = high_time_threshold * 1000   # 30 min for time delta (max time thresh in hysteresis)

        self._motor_speed_delta = delta_motor_speed  # 90 degree step for each increase/decrease in velocity
        self._min_motor_speed = min_motor_speed
        self._max_motor_speed = 720  # based on modular_client max motor speed
        self._min_motor_acc = min_motor_acceleration
        self._max_motor_acc = max_motor_acceleration
        self._motor_acc_delta = delta_motor_acceleration
        self._motor_dec = motor_deceleration
        self._t0 = None

        super(JaneliaAdaptiveSleepDepStimultor, self).__init__(hardware_connection, velocity_threshold, date_range=date_range)

    def _decide(self):
        roi_id = self._tracker._roi.idx
        now = self._tracker.last_time_point

        try:
            channel = self._roi_to_channel[roi_id]
            board = self._roi_to_motor_board[roi_id]
        except KeyError:
            return HasInteractedVariable(False), {}

        has_moved = self._has_moved()
        current_velocity = self._get_velocity()
        # # fly velocity range: 0.0 ->  1.0 with 0.0001 step
        # # rotation speed range: 0.0 -> 100 with 0.01 step
        # # the lower the speed the more velocity
        # speed = round(100.0-(current_velocity * 100.0))

        # Use degree/s for speed instead of steps
        # fly velocity range: 0.0 ->  1.0 with 0.0001 step
        # rotation speed range: 0.0 -> 360 with 1 step
        # the lower the speed the more velocity
        #print(current_velocity)
        current_velocity = 1 if current_velocity > 1 else current_velocity
        current_velocity = 0 if current_velocity < 0 else current_velocity 
        
        #speed = 360 - self._motor_speed[int(current_velocity * 10000)]

        if self._t0 is None:
            self._t0 = now

        if not has_moved:
            if float(now - self._t0) > self._inactivity_time_threshold_ms:
                self._t0 = None
                speed = self._roi_stimulus_status[roi_id]['s']
                acc = self._roi_stimulus_status[roi_id]['a']
                # Check the previous status of the stimulus if the fly was asleep in the previous recording
                # Stay in the same motor speed unless the fly fell asleep again quickly
                # The hysteresis loop for the stimulus staus
                if float(now - self._roi_stimulus_status[roi_id]['t']) <=  self._inactivity_time_threshold_ms + self._time_delta_min:
                    # increase the speed of the motor until max rotation speed
                    if speed < self._max_motor_speed:
                        speed = min(speed + self._motor_speed_delta, self._max_motor_speed)
                     # increase the acc of the motor untill max acc
                    if acc < self._max_motor_acc:
                        acc = min(acc + self._motor_acc_delta, self._max_motor_acc)
                elif float(now - self._roi_stimulus_status[roi_id]['t']) >= self._inactivity_time_threshold_ms + self._time_delta_max:
                    # reduce the speed of the motor until min rotation speed
                    if speed > self._min_motor_speed:
                        speed = max(speed - self._motor_speed_delta, self._min_motor_speed)
                    # reduce the acc of the motor until min acc
                    if acc > self._min_motor_acc:
                        acc = max(acc - self._motor_acc_delta, self._min_motor_acc)

                # update the stimulus status of the roi
                self._roi_stimulus_status[roi_id] = {'t': now, 'v': current_velocity, 's': speed, 'a': acc}
                #print('%d, board%d, channel%d, velocity%f, speed%d, acc%d' %(now, board, channel, current_velocity, speed, acc))
                reported_velocity = round(log10(current_velocity)*1000) if current_velocity > 0 else 0
                return HasInteractedVariable(True), {"board": board, "channel": channel, 'speed': speed, 'velocity':reported_velocity, "acceleration":acc, "deceleration":self._motor_dec}
        else:
            self._t0 = now
        return HasInteractedVariable(False), {}


class JaneliaShakerSleepDepStimultor(IsMovingStimulator):
    _description = {"overview": "A shaker stimulator to sleep deprive an animal using stepper motors.",
                    "arguments": [
                                    {"type": "number", "min": 0.0, "max": 1.0, "step":0.0001, "name": "velocity_threshold", "description": "The minimal velocity that counts as movement","default":0.0060},
                                    {"type": "number", "min": 1, "max": 3600*12, "step":1, "name": "min_inactive_time", "description": "The minimal time after which an inactive animal is awaken","default":120},
                                    {"type": "number", "min": 10, "max": 720 , "step": 1, "name": "motor_speed","description": "The motor speed in degree/sec", "default": 180},
                                    {"type": "date_range", "name": "date_range",
                                     "description": "A date and time range in which the device will perform (see http://tinyurl.com/jv7k826)",
                                     "default": ""},
                                   ]}

    _HardwareInterfaceClass = JaneliaShakerSleepDepriverInterface
    _roi_to_channel = {  # TODO: check if the roi and channel mapping are the same with the second rpi
        1: 6,
        2: 5,
        3: 4,
        4: 3,
        5: 2,
        6: 1,
        7: 0,
        8: 6,
        9: 5,
        10: 4,
        11: 3,
        12: 2,
        13: 1,
        14: 0
    }
    _roi_to_motor_board = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 1,
        13: 1,
        14: 1
    }

    def __init__(self,
                 hardware_connection,
                 velocity_threshold=0.0060,
                 min_inactive_time=120,
                 motor_speed=180,
                 date_range=""):

        """
        A stimulator to control a sleep depriver module.

        :param hardware_connection: the shaker sleep depriver module hardware interface
        :type hardware_connection: :class:`~ethoscope.hardware.interfaces.janelia_sleep_depriver_interface.JaneliaShakerSleepDepriverInterface`
        :param velocity_threshold:
        :type velocity_threshold: float
        :param min_inactive_time: the minimal time without motion after which an animal should be disturbed (in seconds)
        :type min_inactive_time: float
        :param motor_speed: the motor speed in degree/sec
        :type motor_speed: int
        :return:
        """

        self._inactivity_time_threshold_ms = min_inactive_time * 1000  # so we use ms internally
        self._motor_speed = motor_speed
        self._t0 = None

        super(JaneliaShakerSleepDepStimultor, self).__init__(hardware_connection, velocity_threshold, date_range=date_range)

    def _decide(self):
        roi_id = self._tracker._roi.idx
        now = self._tracker.last_time_point

        try:
            channel = self._roi_to_channel[roi_id]
            board = self._roi_to_motor_board[roi_id]
        except KeyError:
            return HasInteractedVariable(False), {}

        has_moved = self._has_moved()
        current_velocity = self._get_velocity()

        current_velocity = 1 if current_velocity > 1 else current_velocity
        current_velocity = 0 if current_velocity < 0 else current_velocity

        if self._t0 is None:
            self._t0 = now

        if not has_moved:
            if float(now - self._t0) > self._inactivity_time_threshold_ms:
                self._t0 = None
                reported_velocity = round(log10(current_velocity)*1000) if current_velocity > 0 else 0
                return HasInteractedVariable(True), {"board": board, "channel": channel, 'speed': self._motor_speed, 'velocity':reported_velocity, "acceleration":10000, "deceleration":10000}
        else:
            self._t0 = now
        return HasInteractedVariable(False), {}


class JaneliaOptoMotorAdaptiveSleepDepStimulator(IsMovingStimulatorDouble):
    _description = {"overview": "An adaptive stimulator to sleep deprive an animal using stepper motors.",
                    "arguments": [
                                    {"type": "number", "min": 0.0, "max": 1.0, "step": 0.0001, "name": "velocity_threshold", "description": "The minimal velocity that counts as movement", "default": 0.0060},
                                    {"type": "number", "min": 1, "max": 3600 * 12, "step": 1, "name": "min_inactive_time", "description": "The minimal time after which an inactive animal is awaken", "default": 120},
                                    {"type": "number", "min": 10, "max": 720, "step": 1, "name": "min_motor_speed", "description": "The motor speed in degree/sec", "default": 180},
                                    {"type": "number", "min": 10, "max": 720, "step": 1, "name": "delta_motor_speed", "description": "The increase/decrease in motor speed", "default": 90},
                                    {"type": "number", "min": 100, "max": 10000, "step": 1, "name": "min_motor_acceleration", "description": "The minimal motor acceleration", "default": 100},
                                    {"type": "number", "min": 100, "max": 10000, "step": 1, "name": "max_motor_acceleration", "description": "The maximal motor acceleration", "default": 10000},
                                    {"type": "number", "min": 10, "max": 10000, "step": 1, "name": "delta_motor_acceleration", "description": "The increase/decrease in motor acceleration", "default": 10},
                                    {"type": "number", "min": 10, "max": 10000, "step": 1, "name": "motor_deceleration", "description": "The motor deceleration", "default": 10000},
                                    {"type": "number", "min": 60, "max": 5 * 60, "step": 1, "name": "low_time_threshold", "description": "The minimal time threshold to increase the speed if fly falls asleep again quickly", "default": 120},
                                    {"type": "number", "min": 60, "max": 30 * 60, "step": 1, "name": "high_time_threshold", "description": "The maximal time threshold to decrease the speed if fly does not fall asleep quickly", "default": 60 * 30},
                                    {"type": "date_range", "name": "date_range", "description": "A date and time range in which the device will perform (see http://tinyurl.com/jv7k826)", "default": ""},
                                    {"type": "date_range", "name": "date_range2", "description": "A date and time range in which the external backlight controller will operate", "default": ""},
                                    ]}

    _HardwareInterfaceClass = JaneliaAdaptiveSleepDepriverInterface
    _roi_to_channel = {  # TODO: check if the roi and channel mapping are the same with the second rpi
        1: 6,
        2: 5,
        3: 4,
        4: 3,
        5: 2,
        6: 1,
        7: 0,
        8: 6,
        9: 5,
        10: 4,
        11: 3,
        12: 2,
        13: 1,
        14: 0
    }
    _roi_to_motor_board = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 1,
        13: 1,
        14: 1
    }

    # Linearly space the motor speed from 0 to 360 into 10000 steps to match the fly velocity
    # _motor_speed = [round(x) for x in np.linspace(0, 360, 10000+1)]

    # Create dictionary of current fly_velocity/motor_speed status for each roi
    _stimulus_info = {'t': 0, 'v': 0.006, 's': 90, 'a': 100}  # initialize the stimulus info for each roi
    _roi_stimulus_status = {1: _stimulus_info,
                            2: _stimulus_info,
                            3: _stimulus_info,
                            4: _stimulus_info,
                            5: _stimulus_info,
                            6: _stimulus_info,
                            7: _stimulus_info,
                            8: _stimulus_info,
                            9: _stimulus_info,
                            10: _stimulus_info,
                            11: _stimulus_info,
                            12: _stimulus_info,
                            13: _stimulus_info,
                            14: _stimulus_info
                            }

    # _time_delta_min = 1000 * 60 * 2       # 2 min for time delta (min time thresh in hysteresis)
    # _time_delta_max = 1000 * 60 * 30      # 30 min for time delta (max time thresh in hysteresis)
    #
    # _motor_speed_delta = 90      # 360 degree step for each increase/decrease in velocity
    # _min_motor_speed = 90
    # _max_motor_speed = 720      # based on modular_client max motor speed
    # _min_motor_acc = 100
    # _max_motor_acc = 10000
    #

    def __init__(self,
                 hardware_connection,
                 velocity_threshold=0.0060,
                 min_inactive_time=120,
                 min_motor_speed=180,
                 delta_motor_speed=90,
                 min_motor_acceleration=100,
                 max_motor_acceleration=10000,
                 delta_motor_acceleration=10,
                 motor_deceleration=10000,
                 low_time_threshold=120,
                 high_time_threshold=1800,
                 date_range="",
                 date_range2=""):
        """
        A stimulator to control a sleep depriver module and an external backlight stimulator.

        :param hardware_connection: the adaptive sleep depriver module hardware interface
        :type hardware_connection: :class:`~ethoscope.hardware.interfaces.janelia_sleep_depriver_interface.JaneliaAdaptiveSleepDepriverInterface`
        :param velocity_threshold:
        :type velocity_threshold: float
        :param min_inactive_time: the minimal time without motion after which an animal should be disturbed (in seconds)
        :type min_inactive_time: float
        :param min_motor_speed: the minimal motor speed in degree/sec
        :type min_motor_speed: int
        :param delta_motor_speed: the increase/decrease in motor speed
        :type delta_motor_speed: int
        :param min_motor_acceleration: the minimal motor acceleration in degree/sec^2
        :type min_motor_acceleration: int
        :param max_motor_acceleration: the maximal motor acceleration in degree/sec^2
        :type max_motor_acceleration: int
        :param delta_motor_acceleration: the increase/decrease in degree/sec^2
        :type delta_motor_acceleration: int
        :param motor_deceleration: the motor deceleration in degree/sec^2
        :type motor_deceleration: int
        :param low_time_threshold: the minimal time the fly falls back to sleep before increasing the speed and acceleration
        :type low_time_threshold: int
        :param high_time_threshold: the maximal time the fly falls back to sleep before decreasing the speed and acceleration
        :type high_time_threshold: int
        :return:
        """

        self._inactivity_time_threshold_ms = min_inactive_time * 1000  # so we use ms internally

        self._time_delta_min = low_time_threshold * 1000  # 2 min for time delta (min time thresh in hysteresis)
        self._time_delta_max = high_time_threshold * 1000  # 30 min for time delta (max time thresh in hysteresis)

        self._motor_speed_delta = delta_motor_speed  # 90 degree step for each increase/decrease in velocity
        self._min_motor_speed = min_motor_speed
        self._max_motor_speed = 720  # based on modular_client max motor speed
        self._min_motor_acc = min_motor_acceleration
        self._max_motor_acc = max_motor_acceleration
        self._motor_acc_delta = delta_motor_acceleration
        self._motor_dec = motor_deceleration
        self._t0 = None

        super(JaneliaOptoMotorAdaptiveSleepDepStimulator, self).__init__(hardware_connection, velocity_threshold,
                                                               date_range=date_range, date_range2=date_range2)

    def _decide(self):
        roi_id = self._tracker._roi.idx
        now = self._tracker.last_time_point

        try:
            channel = self._roi_to_channel[roi_id]
            board = self._roi_to_motor_board[roi_id]
        except KeyError:
            return HasInteractedVariable(False), {}

        has_moved = self._has_moved()
        current_velocity = self._get_velocity()
        # # fly velocity range: 0.0 ->  1.0 with 0.0001 step
        # # rotation speed range: 0.0 -> 100 with 0.01 step
        # # the lower the speed the more velocity
        # speed = round(100.0-(current_velocity * 100.0))

        # Use degree/s for speed instead of steps
        # fly velocity range: 0.0 ->  1.0 with 0.0001 step
        # rotation speed range: 0.0 -> 360 with 1 step
        # the lower the speed the more velocity
        # print(current_velocity)
        current_velocity = 1 if current_velocity > 1 else current_velocity
        current_velocity = 0 if current_velocity < 0 else current_velocity

        # speed = 360 - self._motor_speed[int(current_velocity * 10000)]

        if self._t0 is None:
            self._t0 = now

        if not has_moved:
            if float(now - self._t0) > self._inactivity_time_threshold_ms:
                self._t0 = None
                speed = self._roi_stimulus_status[roi_id]['s']
                acc = self._roi_stimulus_status[roi_id]['a']
                # Check the previous status of the stimulus if the fly was asleep in the previous recording
                # Stay in the same motor speed unless the fly fell asleep again quickly
                # The hysteresis loop for the stimulus staus
                if float(now - self._roi_stimulus_status[roi_id][
                    't']) <= self._inactivity_time_threshold_ms + self._time_delta_min:
                    # increase the speed of the motor until max rotation speed
                    if speed < self._max_motor_speed:
                        speed = min(speed + self._motor_speed_delta, self._max_motor_speed)
                    # increase the acc of the motor untill max acc
                    if acc < self._max_motor_acc:
                        acc = min(acc + self._motor_acc_delta, self._max_motor_acc)
                elif float(now - self._roi_stimulus_status[roi_id][
                    't']) >= self._inactivity_time_threshold_ms + self._time_delta_max:
                    # reduce the speed of the motor until min rotation speed
                    if speed > self._min_motor_speed:
                        speed = max(speed - self._motor_speed_delta, self._min_motor_speed)
                    # reduce the acc of the motor until min acc
                    if acc > self._min_motor_acc:
                        acc = max(acc - self._motor_acc_delta, self._min_motor_acc)

                # update the stimulus status of the roi
                self._roi_stimulus_status[roi_id] = {'t': now, 'v': current_velocity, 's': speed, 'a': acc}
                # print('%d, board%d, channel%d, velocity%f, speed%d, acc%d' %(now, board, channel, current_velocity, speed, acc))
                reported_velocity = round(log10(current_velocity) * 1000) if current_velocity > 0 else 0
                return HasInteractedVariable(True), {"board": board, "channel": channel, 'speed': speed,
                                                     'velocity': reported_velocity, "acceleration": acc,
                                                     "deceleration": self._motor_dec}
        else:
            self._t0 = now
        return HasInteractedVariable(False), {}

    def _communicate(self, communicate_signal):
        """
        communicate an operating signal to an outside stimulator

        :param communicate_signal: an ON and OFF signal to the external stimulator
        :type communicate_signal: bool
        """
        server_ip = '192.168.123.2'
        tcp_port = 9998
        t = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        name = get_machine_info('/etc/machine-name')
        # msg: timestamp + machine-name + signal(ON-OFF)
        msg = t + '_' + name + '_' + str(communicate_signal)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_ip, tcp_port))
            time.sleep(1)
            s.send(msg)
            s.close()
        except:
            logging.info('Trigger backlight was not successful')



class OptomotorSleepDepriver(SleepDepStimulator):
    _description = {"overview": "A stimulator to sleep deprive an animal using gear motors. See https://github.com/gilestrolab/ethoscope_hardware/tree/master/modules/gear_motor_sleep_depriver",
                    "arguments": [
                                    {"type": "number", "min": 0.0, "max": 1.0, "step":0.0001, "name": "velocity_threshold", "description": "The minimal velocity that counts as movement","default":0.0060},
                                    {"type": "number", "min": 1, "max": 3600*12, "step":1, "name": "min_inactive_time", "description": "The minimal time after which an inactive animal is awaken(s)","default":120},
                                    {"type": "number", "min": 500, "max": 10000 , "step": 50, "name": "pulse_duration", "description": "For how long to deliver the stimulus(ms)", "default": 1000},
                                    {"type": "number", "min": 0, "max": 3, "step": 1, "name": "stimulus_type",  "description": "1 = opto, 2= moto", "default": 2},
                                    {"type": "date_range", "name": "date_range",
                                     "description": "A date and time range in which the device will perform (see http://tinyurl.com/jv7k826)",
                                     "default": ""}
                                   ]}

    _HardwareInterfaceClass = OptoMotor

    _roi_to_channel_opto = {
        1: 1,
        3: 3,
        5: 5,
        7: 7,
        9: 9,
        12: 23,
        14: 21,
        16: 19,
        18: 17,
        20: 15
    }
    _roi_to_channel_moto = {
        1: 0,
        3: 2,
        5: 4,
        7: 6,
        9: 8,
        12: 22,
        14: 20,
        16: 18,
        18: 16,
        20: 14
    }


    def __init__(self,
                 hardware_connection,
                 velocity_threshold=0.0060,
                 min_inactive_time=120,  # s
                 pulse_duration = 1000,  #ms
                 stimulus_type = 2,  # 1 = opto, 2= moto, 3 = both
                 date_range=""
                 ):


        self._t0 = None

        # the inactive time depends on the chanel here
        super(OptomotorSleepDepriver, self).__init__(hardware_connection, velocity_threshold, min_inactive_time, date_range)



        if stimulus_type == 2:
            self._roi_to_channel = self._roi_to_channel_moto
        elif stimulus_type == 1:
            self._roi_to_channel = self._roi_to_channel_opto

        self._pulse_duration= pulse_duration

    def _decide(self):
        out, dic = super(OptomotorSleepDepriver, self)._decide()
        dic["duration"] = self._pulse_duration
        return out,dic


class ExperimentalSleepDepStimulator(SleepDepStimulator):
    _description = {"overview": "A stimulator to sleep deprive an animal using servo motor. See http://todo/fixme.html",
                    "arguments": [
                                    {"type": "number", "min": 0.0, "max": 1.0, "step":0.0001, "name": "velocity_threshold", "description": "The minimal velocity that counts as movement","default":0.0060},
                                    {"type": "date_range", "name": "date_range",
                                     "description": "A date and time range in which the device will perform (see http://tinyurl.com/jv7k826)",
                                     "default": ""}
                                   ]}

    _HardwareInterfaceClass = SleepDepriverInterface
    _roi_to_channel = {
            1:1,  3:2,  5:3,  7:4,  9:5,
            12:6, 14:7, 16:8, 18:9, 20:10
        }

    def __init__(self,
                 hardware_connection,
                 velocity_threshold=0.0060,
                 date_range=""
                 ):
        """
        A stimulator to control a sleep depriver module.
        This is an experimental version where each channel has a different inactivity_time_threshold.

        :param hardware_connection: the sleep depriver module hardware interface
        :type hardware_connection: :class:`~ethoscope.hardawre.interfaces.sleep_depriver_interface.SleepDepriverInterface`
        :param velocity_threshold:
        :type velocity_threshold: float
        :return:
        """

        self._t0 = None

        
        # the inactive time depends on the chanel here
        super(ExperimentalSleepDepStimulator, self).__init__(hardware_connection, velocity_threshold, 0, date_range)
        self._inactivity_time_threshold_ms = None

    # here we override bind tracker so that we also define inactive time for this stimulator
    def bind_tracker(self, tracker):
        self._tracker = tracker

        roi_id = self._tracker._roi.idx
        try:
            channel = self._roi_to_channel[roi_id]
            self._inactivity_time_threshold_ms = round(channel ** 1.7) * 20 * 1000
        except KeyError:
            pass


class MiddleCrossingStimulator(BaseStimulator):
    _description = {"overview": "A stimulator to disturb animal as they cross the midline",
                    "arguments": [
                                    {"type": "number", "min": 0.0, "max": 1.0, "step":0.01, "name": "p", "description": "the probability to move the tube when a beam cross was detected","default":1.0},
                                    {"type": "date_range", "name": "date_range",
                                     "description": "A date and time range in which the device will perform (see http://tinyurl.com/jv7k826)",
                                     "default": ""}
                                   ]}

    _HardwareInterfaceClass = SleepDepriverInterface
    _refractory_period = 60#s
    _roi_to_channel = {
            1:1,  3:2,  5:3,  7:4,  9:5,
            12:6, 14:7, 16:8, 18:9, 20:10
        }
    def __init__(self,
                 hardware_connection,
                 p=1.0,
                 date_range=""
                 ):
        """
        :param hardware_connection: the sleep depriver module hardware interface
        :type hardware_connection: :class:`~ethoscope.hardawre.interfaces.sleep_depriver_interface.SleepDepriverInterface`
        :param p: the probability of disturbing the animal when a beam cross happens
        :type p: float
        :return:
        """

        self._last_stimulus_time = 0
        self._p = p
        
        super(MiddleCrossingStimulator, self).__init__(hardware_connection,  date_range=date_range)

    def _decide(self):
        roi_id = self._tracker._roi.idx
        now = self._tracker.last_time_point
        if now - self._last_stimulus_time < self._refractory_period * 1000:
            return HasInteractedVariable(False), {}

        try:
            channel = self._roi_to_channel[roi_id]
        except KeyError:
            return HasInteractedVariable(False), {}

        positions = self._tracker.positions

        if len(positions) < 2:
            return HasInteractedVariable(False), {}

        if len(positions[-1]) != 1:
            raise Exception("This stimulator can only work with a single animal per ROI")

        roi_w = float(self._tracker._roi.longest_axis)
        x_t_zero = positions[-1][0]["x"] / roi_w - 0.5
        x_t_minus_one = positions[-2][0]["x"] / roi_w - 0.5

        # if roi_id == 12:
        #     print (roi_id, channel, roi_w, positions[-1][0]["x"], positions[-2][0]["x"], x_t_zero, x_t_minus_one)
        if (x_t_zero > 0) ^ (x_t_minus_one >0): # this is a change of sign

            if random.uniform(0,1) < self._p:
                self._last_stimulus_time = now
                return HasInteractedVariable(True), {"channel": channel}

        return HasInteractedVariable(False), {"channel": channel}

