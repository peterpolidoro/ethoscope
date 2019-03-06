# We import all the bricks from ethoscope package
import sys
import time
import random
#from picamera import PiCamera
from ethoscope.core.monitor import Monitor
from ethoscope.utils.io import SQLiteResultWriter
from ethoscope.drawers.drawers import DefaultDrawer
from ethoscope.trackers.adaptive_bg_tracker import AdaptiveBGModel

from ethoscope.hardware.input.cameras import OurPiCameraAsync
#from ethoscope.hardware.input.cameras import MovieVirtualCamera

from ethoscope.stimulators.sleep_depriver_stimulators import JaneliaSleepDepStimultor
#from ethoscope.stimulators.sleep_depriver_stimulators import IsMovingStimulator

# You can also load other types of ROI builder. This one is for 20 tubes (two columns of ten rows)
#from ethoscope.roi_builders.target_roi_builder import SleepMonitorWithTargetROIBuilder
from ethoscope.roi_builders.target_roi_builder import SleepMonitorWithTargetROIBuilderJanelia

from modular_client import ModularClients

#from ethoscope.hardware.interfaces.interfaces import BaseInterface
#from ethoscope.stimulators.stimulators import BaseStimulator, HasInteractedVariable
from ethoscope.hardware.interfaces.interfaces import HardwareConnection
from ethoscope.hardware.interfaces.janelia_sleep_depriver_interface import JaneliaSleepDepriverInterface


#camera = PiCamera()
#camera.resolution = (1640, 1232)
#camera.framerate = 15
# change these three variables according to how you name your input/output files
#INPUT_VIDEO = "arena_10x2_sortTubes.mp4"
#INPUT_VIDEO = "videoNew_h264.mp4"

#INPUT_VIDEO = "videoCoveredtarget_h264.mp4"
OUTPUT_VIDEO = "/tmp/output_etho_motor.avi"
OUTPUT_DB = "/tmp/results_etho_motor.db"


#class ModularClientInterface(BaseInterface):
#    
#    _dev0 = None
#    _dev1 = None
#    
#    def __init__(self, port0=None, port1=None, *args, **kwargs):
#        """
#        Class to connect and abstract the Modular Client stepper controller.
#        
#        :param port1: the serial port to use for first motion controller board. Automatic detection if ``None``.
#        :param port1: the serial port to use for second motion controller board. Automatic detection if ``None``.
#        :param args: additional arguments
#        :param kwargs: additional keyword arguments
#        """
#        
#        print('Connecting to stepper controller ... ')
#        
#        if port0 is None and port1 is None :
#            self._dev0, self._dev1 =  self._find_ports()
#        else:
#            self._dev0 = port0
#            self._dev1 = port1
#    
#        #reset the positions of the motors
#        self._reset_all()
#        
#        super(ModularClientInterface,self).__init__(*args, **kwargs)
#            
#             
#    def _find_ports(self):
#        devs = ModularClients() # Might automatically find device if one available
#        print(devs.items())
#        #TODO: check first that the driver is available before accessing it in the dictionary
#        dev0 = devs['ethoscope_stepper_controller']['5x3'][0]
#        dev1 = devs['ethoscope_stepper_controller']['5x3'][1]
#        
#        return dev0, dev1
#    
#    def _reset_all(self):
#        if self._dev0 is not None and self._dev1 is not None:
#            self._dev0.stop_all()
#            self._dev0.zero_all()
#            self._dev0.acceleration_max('setAllElementValues',10) # fix the acceleration of all the motors at 10
#            
#            self._dev1.stop_all()
#            self._dev1.zero_all()
#            self._dev1.acceleration_max('setAllElementValues',10) # fix the acceleration of all the motors at 10
#        else:
#            raise Exception("Could not initialize the motor boards.")
#        
#    
#    
#    def move_with_speed(self, board, channel, speed=0, duration=1000):
#        """
#        Move a specified rotation to a speed for a certain time.
#
#        :param board: the board number (0 or 1)
#        :type channel: int
#        :param channel: the number of the stepper motor to be moved
#        :type channel: int
#        :param speed: the speed, between -100 and 100. The sign indicates the rotation direction (CW or CCW)
#        :type speed: int 
#        :param duration: the time (ms) the stimulus should last
#        :type duration: int
#        :return:
#        """
#        
#        if channel < 0 or channel > 6:
#            raise Exception("idx channel must be between 0 and 6")
#        
#        if board < 0 or board > 1:
#            raise Exception("idx board must be 0 or 1")
#        
#        if board == 0:
#            motor = self._dev0
#        elif board == 1:
#            motor = self._dev1
#        
#        #TODO: fix the duration: This should be done as a timer on the motor board
#        motor.move_at(channel, speed)
#        time.sleep(float(duration)/1000.0)
#        motor.stop(channel) 
#        return
#    
#    def send(self, *args, **kwargs):
#        """
#        The default sending paradigm is empty
#        """
#        #raise NotImplementedError
#        pass
#        
#    def _warm_up(self):
#        """
#        This will move all motors.
#        Useful for testing
#        """
#        #for i in range(1, 1 + self._n_channels):
#        #    self.send(i)
#        self._dev0.move_all_at(30)
#        self._dev1.move_all_at(30)
#        time.sleep(2)
#        self._dev0.stop_all()
#        self._dev1.stop_all()
#        self._dev0.zero_all()
#        self._dev1.zero_all()
#        
#
#
#class JaneliaSleepDepriverInterface(ModularClientInterface):
#    def send(self, board, channel):
#        """
#        Sleep deprive an animal by rotating its tube.
#
#        :param board: the board number (0 or 1)
#        :type channel: int
#        :param channel: the number of the stepper motor to be moved
#        :type channel: int
#        :param speed: the speed, between -100 and 100. The sign indicates the rotation direction (CW or CCW)
#        :type speed: int 
#        """
#        speed = 100 # max speed for now. #TODO: make this configurable in the send command
#        self.move_with_speed(board, channel)
#
#        
#class JaneliaSleepDepStimultor(IsMovingStimulator):
#    _HardwareInterfaceClass = JaneliaSleepDepriverInterface
#    _roi_to_channel = { #TODO: check if the roi and  channel is the same when the second 
#            1:6, 2:5, 3:4, 4:3, 5:2, 6:1, 7:0,
#            8:6, 9:5, 10:4, 11:3, 12:2, 13:1, 14:0
#        }
#    _roi_to_motor_board = {
#            1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0,
#            8:1, 9:1, 10:1, 11:1, 12:1, 13:1, 14:1
#        }
#    
#    def __init__(self,
#                 hardware_connection,
#                 velocity_threshold=0.0060,
#                 min_inactive_time=120, #s
#                 date_range=""):
#        """
#        A stimulator to control a sleep depriver module.
#
#        :param hardware_connection: the sleep depriver module hardware interface
#        :type hardware_connection: :class:`~ethoscope.hardware.interfaces.sleep_depriver_interface.SleepDepriverInterface`
#        :param velocity_threshold:
#        :type velocity_threshold: float
#        :param min_inactive_time: the minimal time without motion after which an animal should be disturbed (in seconds)
#        :type min_inactive_time: float
#        :return:
#        """
#
#        self._inactivity_time_threshold_ms = min_inactive_time *1000 #so we use ms internally
#        self._t0 = None
#        
#        super(JaneliaSleepDepStimultor, self).__init__(hardware_connection, velocity_threshold, date_range=date_range)
#
#
#
#    def _decide(self):
#        roi_id= self._tracker._roi.idx
#        now =  self._tracker.last_time_point
#
#        try:
#            channel = self._roi_to_channel[roi_id]
#            board = self._roi_to_motor_board[roi_id]
#        except KeyError:
#            return HasInteractedVariable(False), {}
#
#        has_moved = self._has_moved()
#
#
#        if self._t0 is None:
#            self._t0 = now
#
#        if not has_moved:
#            if float(now - self._t0) > self._inactivity_time_threshold_ms:
#                self._t0 = None
#                return HasInteractedVariable(True), {"board":board, "channel":channel}  #speed is fixed now at 100
#        else:
#            self._t0 = now
#        return HasInteractedVariable(False), {}
    
    

##class MockInterface(BaseInterface):
##    def send(self,**kwargs):
##        print("Sending " + str(kwargs))
##        time.sleep(.1)
##    def _warm_up(self):
##        print("Warming up")
##        time.sleep(1)
##
##class MockStimulator(BaseStimulator):
##    _HardwareInterfaceClass = MockInterface
##    def _decide(self):
##        roi_id = self._tracker._roi.idx
##        now = self._tracker.last_time_point
##        # every 100 times:
##        interact = random.uniform(0.0, 1.0) < 0.01
##        return HasInteractedVariable(interact), {"channel":roi_id, "time":now }


# We use a video input file as if it was a "camera"
#cam = MovieVirtualCamera(INPUT_VIDEO)
#target_fps=20, target_resolution=(1280,960)
cam = OurPiCameraAsync()
#print(cam)
# here, we generate ROIs automatically from the targets in the images
roi_builder = SleepMonitorWithTargetROIBuilderJanelia()
#roi_builder = SleepMonitorWithTargetROIBuilder(n_rows=7, n_cols=2)
rois = roi_builder.build(cam)
# Build the stimulator
hc = HardwareConnection(JaneliaSleepDepriverInterface)
stimulators = [JaneliaSleepDepStimultor(hc) for _ in rois]

# Then, we go back to the first frame of the video
cam.restart()

# we use a drawer to show inferred position for each animal, display frames and save them as a video
drawer = DefaultDrawer(OUTPUT_VIDEO, draw_frames = False)

# We build our monitor
monitor = Monitor(cam, AdaptiveBGModel, rois, stimulators)

try:
    # Now everything is ready, we run the monitor with a result writer and a drawer
    with SQLiteResultWriter(OUTPUT_DB, rois) as rw:
         monitor.run(rw,drawer)
    
finally:
    hc.stop()
    cam._close()     
    print('----Put the motor controller in low power mode----')
    devs = ModularClients()  # Might automatically find device if one available
    #print(devs.items())
    if devs is not None:
        dev0 = devs['ethoscope_stepper_controller']['5x3'][0]
        dev1 = devs['ethoscope_stepper_controller']['5x3'][1]
        dev0.sleep_all()
        dev1.sleep_all()
    else:
        raise Exception ('Could not put motor controllers to sleep')
            