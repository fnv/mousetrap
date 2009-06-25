"""
    Demo application that implements the CamShift IDM (Image Detection Module)
    to track colors from a webcam.
"""

from ocvfw.dev.camera import Camera, Capture, Point

class Module(object):
    
    def __init__(self):
        
        # By Flavio's design, the modules themselves initialize the camera
        Camera.init()
    
    def set_capture(self, cam):
        """
        Arguments:
            cam : Camera device index
        """
        self.cap = Capture(async=True, idx=cam)
        self.cap.change(color="rgb", flip=True)
    
    def get_image():
        """
        Guys, this function is mandatory. Must return IPLimage or CVmat thingy
        """