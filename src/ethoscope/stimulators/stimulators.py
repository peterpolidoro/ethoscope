__author__ = 'quentin'

from ethoscope.utils.description import DescribedObject
from ethoscope.core.variables import BaseIntVariable
from ethoscope.hardware.interfaces.interfaces import DefaultInterface
from ethoscope.utils.scheduler import Scheduler

import datetime
import socket
import sys

class HasInteractedVariable(BaseIntVariable):
    """
    Custom variable to save whether the stimulator has sent instruction to its hardware interface. 0 means
     no interaction. Any positive integer describes a different interaction.
    """
    functional_type = "interaction"
    header_name = "has_interacted"



class BaseStimulator(DescribedObject):
    _tracker = None
    _HardwareInterfaceClass = None

    def __init__(self, hardware_connection, date_range=""):  #Janelia adds another date range for the second date_range
        """
        Template class to interact with the tracked animal in a real-time feedback loop.
        Derived classes must have an attribute ``_hardwareInterfaceClass`` defining the class of the
        :class:`~ethoscope.hardware.interfaces.interfaces.BaseInterface` object (not on object) that instances will
        share with one another. In addition, they must implement a ``_decide()`` method.

        :param hardware_connection: The hardware interface to use.
        :type hardware_connection: :class:`~ethoscope.hardware.interfaces.interfaces.BaseInterface`
        :param date_range: the start and stop date/time for the stimulator. Format described `here <https://github.com/gilestrolab/ethoscope/blob/master/user_manual/schedulers.md>`_
        :type date_range: str
        """

        self._scheduler = Scheduler(date_range)
        self._hardware_connection = hardware_connection

    def apply(self):
        """
        Apply this stimulator. This method will:

        1. check ``_tracker`` exists
        2. decide (``_decide``) whether to interact
        3. if 2. pass the interaction arguments to the hardware interface
        
        :return: whether a stimulator has worked, and a result dictionary
        """
        if self._tracker is None:
            raise ValueError("No tracker bound to this stimulator. Use `bind_tracker()` methods")

        if self._scheduler.check_time_range() is False:
            return HasInteractedVariable(False) , {}
        interact, result = self._decide()
        if interact > 0:
            self._deliver(**result)

        return interact, result


    def bind_tracker(self, tracker):
        """
        Link a tracker to this interactor

        :param tracker: a tracker object.
        :type tracker: :class:`~ethoscope.trackers.trackers.BaseTracker`
        """
        self._tracker = tracker

    def _decide(self):
        raise NotImplementedError

    def _deliver(self, **kwargs):
        if self._hardware_connection is not None:
            self._hardware_connection.send_instruction(kwargs)

    # Janelia returns type of stimulator
    def stimulator_type(self):
        return 'Base'


class DoubleBaseStimulator(DescribedObject):
    _tracker = None
    _HardwareInterfaceClass = None
    _socket_handler = None

    def __init__(self, hardware_connection, date_range="", date_range2=""):
        """
        Template class to interact with the tracked animal in a real-time feedback loop with two stimulus.
        The first stimulus is a controlled stimulus from the RPi and the second stimulus is an external stimulus that
        has its own protocol but only needs an ON and OFF signal

        Derived classes must have an attribute ``_hardwareInterfaceClass`` defining the class of the
        :class:`~ethoscope.hardware.interfaces.interfaces.BaseInterface` object (not on object) that instances will
        share with one another. In addition, they must implement a ``_decide()`` method.

        :param hardware_connection: The hardware interface to use.
        :type hardware_connection: :class:`~ethoscope.hardware.interfaces.interfaces.BaseInterface`
        :param date_range: the start and stop date/time for the stimulator. Format described `here <https://github.com/gilestrolab/ethoscope/blob/master/user_manual/schedulers.md>`_
        :type date_range: str
        :param date_range2: the start and stop date/time for the second stimulator. Format described `here <https://github.com/gilestrolab/ethoscope/blob/master/user_manual/schedulers.md>`_
        :type date_range: str
        """

        self._scheduler = Scheduler(date_range)
        self._scheduler2 = Scheduler(date_range2)
        self._hardware_connection = hardware_connection
        self._communicationflag=False

        _server_ip = '192.168.123.2'  # node ip
        _tcp_port = 9998

        try:
            _socket_handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket_handler.connect((_server_ip, _tcp_port))
        except socket.error, exc:
            print "Caught exception socket.error : %s" % exc


    def apply(self):
        """
        Apply this stimulator. This method will:

        1. check ``_tracker`` exists
        2. decide (``_decide``) whether to interact
        3. if 2. pass the interaction arguments to the hardware interface

        :return: whether a stimulator has worked, and a result dictionary
        """
        if self._tracker is None:
            raise ValueError("No tracker bound to this stimulator. Use `bind_tracker()` methods")

        # check the second time range for the second stimulus
        if self._scheduler2.check_time_range() is True and self._communicationflag is False:
            #print('Scheduler 2 is ON now:'+datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
            self._communicate(True) # send an On Signal
            self._communicationflag = True
        elif self._scheduler2.check_time_range() is False and self._communicationflag is True:
            #print('Scheduler 2 is OFF now:'+datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
            self._communicate(False)  # send an OFF Signal
            self._communicationflag = False

        if self._scheduler.check_time_range() is False:
            return HasInteractedVariable(False), {}
        #print('Scheduler 1 is active now:'+datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
        interact, result = self._decide()
        if interact > 0:
            self._deliver(**result)

        return interact, result

    def bind_tracker(self, tracker):
        """
        Link a tracker to this interactor

        :param tracker: a tracker object.
        :type tracker: :class:`~ethoscope.trackers.trackers.BaseTracker`
        """
        self._tracker = tracker

    def _decide(self):
        raise NotImplementedError


    def _deliver(self, **kwargs):
        if self._hardware_connection is not None:
            self._hardware_connection.send_instruction(kwargs)


    def _communicate(self, communicate_signal):
        """
        communicate an operating signal to an outside stimulator

        :param communicate_signal: an ON and OFF signal to the external stimulator
        :type communicate_signal: bool
        """
        raise NotImplementedError


    def get_socket_handler(self):
        """
            get the socket handler for the second stimulator
        """
        return self._socket_handler


    # Janelia returns type of stimulator
    def stimulator_type(self):
        return 'Double'


class DefaultStimulator(BaseStimulator):
    """
    Default interactor. Simply never interacts
    """
    _description = {"overview": "The default 'interactor'. To use when no hardware interface is to be used.",
                    "arguments": []}
    _HardwareInterfaceClass = DefaultInterface

    def _decide(self):
        out = HasInteractedVariable(False)
        return out, {}

    # Janelia returns type of stimulator
    def stimulator_type(self):
        return 'Base'


