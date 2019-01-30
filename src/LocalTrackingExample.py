# We import all the bricks from ethoscope package
import sys
#from picamera import PiCamera
#print(sys.path)
from ethoscope.core.monitor import Monitor
from ethoscope.trackers.adaptive_bg_tracker import AdaptiveBGModel
from ethoscope.utils.io import SQLiteResultWriter
from ethoscope.hardware.input.cameras import MovieVirtualCamera
from ethoscope.hardware.input.cameras import OurPiCameraAsync
from ethoscope.drawers.drawers import DefaultDrawer

# You can also load other types of ROI builder. This one is for 20 tubes (two columns of ten rows)
from ethoscope.roi_builders.target_roi_builder import SleepMonitorWithTargetROIBuilder
from ethoscope.roi_builders.target_roi_builder import SleepMonitorWithTargetROIBuilderJanelia
from modular_client import ModularClient



#camera = PiCamera()
#camera.resolution = (1640, 1232)
#camera.framerate = 15
# change these three variables according to how you name your input/output files
#INPUT_VIDEO = "arena_10x2_sortTubes.mp4"
#INPUT_VIDEO = "videoNew_h264.mp4"

#INPUT_VIDEO = "videoCoveredtarget_h264.mp4"
OUTPUT_VIDEO = "/tmp/my_output_new_etho_covered.avi"
OUTPUT_DB = "/tmp/results_new_etho.db"

# Initialize the modular motors
dev = ModularClient() # Might automatically find device if one available
id = dev.get_device_id()
methods = dev.get_methods()
print(id)
print(methods)


# We use a video input file as if it was a "camera"
#cam = MovieVirtualCamera(INPUT_VIDEO)
#target_fps=20, target_resolution=(1280,960)
cam = OurPiCameraAsync()
#print(cam)
# here, we generate ROIs automatically from the targets in the images
roi_builder = SleepMonitorWithTargetROIBuilderJanelia()
#roi_builder = SleepMonitorWithTargetROIBuilder(n_rows=7, n_cols=2)
rois = roi_builder.build(cam)
# Then, we go back to the first frame of the video
cam.restart()

# we use a drawer to show inferred position for each animal, display frames and save them as a video
drawer = DefaultDrawer(OUTPUT_VIDEO, draw_frames = True)
# We build our monitor
monitor = Monitor(cam, AdaptiveBGModel, rois)

# Now everything is ready, we run the monitor with a result writer and a drawer
with SQLiteResultWriter(OUTPUT_DB, rois) as rw:
     monitor.run(rw,drawer)
