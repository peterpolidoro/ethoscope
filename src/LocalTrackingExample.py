# We import all the bricks from ethoscope package
import sys
#from picamera import PiCamera
from ethoscope.core.monitor import Monitor
from ethoscope.trackers.adaptive_bg_tracker import AdaptiveBGModel
from ethoscope.utils.io import SQLiteResultWriter
from ethoscope.hardware.input.cameras import MovieVirtualCamera
from ethoscope.hardware.input.cameras import OurPiCameraAsync
from ethoscope.drawers.drawers import DefaultDrawer
from ethoscope.stimulators.sleep_depriver_stimulators import SleepDepStimulator
from ethoscope.hardware.interfaces.sleep_depriver_interface import SleepDepriverInterface

# You can also load other types of ROI builder. This one is for 20 tubes (two columns of ten rows)
#from ethoscope.roi_builders.target_roi_builder import SleepMonitorWithTargetROIBuilder

from ethoscope.roi_builders.target_roi_builder import SleepMonitorWithTargetROIBuilderJanelia
from modular_client import ModularClients
from ethoscope.stimulators.stimulators import BaseStimulator, HasInteractedVariable
from ethoscope.hardware.interfaces.interfaces import BaseInterface
from ethoscope.hardware.interfaces.interfaces import HardwareConnection

#camera = PiCamera()
#camera.resolution = (1640, 1232)
#camera.framerate = 15
# change these three variables according to how you name your input/output files
#INPUT_VIDEO = "arena_10x2_sortTubes.mp4"
#INPUT_VIDEO = "videoNew_h264.mp4"

#INPUT_VIDEO = "videoCoveredtarget_h264.mp4"
OUTPUT_VIDEO = "/tmp/my_output_new_etho_covered.avi"
OUTPUT_DB = "/tmp/results_new_etho.db"


class MockInterface(BaseInterface):
    def send(self,**kwargs):
        print("Sending " + str(kwargs))
        time.sleep(.1)
    def _warm_up(self):
        print("Warming up")
        time.sleep(1)

class MockStimulator(BaseStimulator):
    _HardwareInterfaceClass = MockInterface
    def _decide(self):
        roi_id = self._tracker._roi.idx
        now = self._tracker.last_time_point
        # every 100 times:
        interact = random.uniform(0.0, 1.0) < 0.01
        return HasInteractedVariable(interact), {"channel":roi_id, "time":now }



# Initialize the modular motors
devs = ModularClients() # Might automatically find device if one available
print(devs.items())

dev0 = devs['ethoscope_stepper_controller']['5x3'][0]
dev1 = devs['ethoscope_stepper_controller']['5x3'][1]

dev0.channel_count()


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
hc = HardwareConnection(MockInterface)
stimulators = [MockStimulator(hc) for _ in rois]

# Then, we go back to the first frame of the video
cam.restart()

# we use a drawer to show inferred position for each animal, display frames and save them as a video
drawer = DefaultDrawer(OUTPUT_VIDEO, draw_frames = True)

# We build our monitor
monitor = Monitor(cam, AdaptiveBGModel, rois, stimulators)

try:
    # Now everything is ready, we run the monitor with a result writer and a drawer
    with SQLiteResultWriter(OUTPUT_DB, rois) as rw:
         monitor.run(rw,drawer)
     
finally:
    hc.stop()
    cam._close()     
