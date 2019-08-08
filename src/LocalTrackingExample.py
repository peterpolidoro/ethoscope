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

# We use a video input file as if it was a "camera"
#cam = MovieVirtualCamera(INPUT_VIDEO)
#target_fps=20, target_resolution=(1280,960)
cam = OurPiCameraAsync()

# here, we generate ROIs automatically from the targets in the images
roi_builder = SleepMonitorWithTargetROIBuilderJanelia()
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
    if devs is not None:
        dev0 = devs['ethoscope_stepper_controller']['5x3'][0]
        dev1 = devs['ethoscope_stepper_controller']['5x3'][1]
        dev0.sleep_all()
        dev1.sleep_all()
    else:
        raise Exception ('Could not put motor controllers to sleep')
            