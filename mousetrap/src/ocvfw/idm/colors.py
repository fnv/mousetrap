# -*- coding: utf-8 -*-

# Ocvfw
#
# Copyright 2009 Flavio Percoco Premoli
#
# This file is part of Ocvfw.
#
# Ocvfw is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v2 as published
# by the Free Software Foundation.
#
# Ocvfw is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ocvfw.  If not, see <http://www.gnu.org/licenses/>>.


"""Color-tracking IDM"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import ocvfw.commons as commons
from ocvfw.dev.camera import Camera, Capture, Point
from ctypes import c_int
from ctypesopencv import *
from sys import argv, exit
import math

# IDM's Information
# a_name: IDM's name
#   This is used by the settings gui to identify the idm
# a_description: IDM's Description
# a_settings: Possible settings needed by the idm. For Example: { 'var_name' : { 'value' : default_value}, 'var_name2' : { 'value' : default_value} }
a_name = "colors"
a_description = "Color tracker based on CAMshift algorithm"
a_settings = {}

class Module(object):
    """
    This is the IDM's Main class, called by mousetrap.py in the load process.
    """

    def __init__(self, controller, stgs = {}):
        """
        IDM's init function.
        
        Arguments:
        - self: The main object pointer.
        - controller: mousetrap main class pointer. This is passed by MouseTrap's controller (mousetrap.py) when loaded.
        - stgs: Possible settings loaded from the user's settings file. If there aren't settings the IDM will use the a_settings dict.
        """
        
        # This will init the Camera class. 
        # This class is used to handle the camera device.
        Camera.init()

        # Controller instance
        self.ctr          = controller
        
        # Capture instance
        # The capture is the object containing the image 
        # and all the possible methods to modify it.
        self.cap          = None
        
        # IDM's Settings dict
        self.stgs         = stgs

        # Prepares the IDM using the settings.
        self.prepare_config()

    def prepare_config(self):
        """
        Prepares the IDM using the settings
        
        Arguments:
        - self: The main object pointer
        """
        global a_settings
        
        # If the dict is empty then 
        # use the default settings defined in a_settings
        if not self.stgs:
            self.stgs = a_settings

        # For each key do something if required by the module
        for key in self.stgs:
            pass

        image = None
        hsv = None
        hue = None
        mask = None
        backproject = None
        histimg = None
        hist = None

        backproject_mode = 0
        select_object = 0
        track_object = 0
        show_hist = 1
        origin = None
        selection = None
        track_window = None
        track_box = None
        track_comp = None
        hdims = 16

       # initial settings for value, saturation, and hue
        vmin = c_int(10)
        vmax = c_int(256)
        smin = c_int(80)
        smax = c_int(256)
        hmin = c_int(25)
        hmax = c_int(40) #this may have to be 180 and not 256, for whatever reason
        h2min = c_int(170)
        h2max = c_int(175)

    def on_mouse(event, x, y, flags, param):
        global select_object, image, selection, origin, track_object
    
        if image is None:
            return

        if image.origin:
            y = image.height - y

        if select_object:
            selection.x = min(x,origin.x)
            selection.y = min(y,origin.y)
            selection.width = selection.x + abs(x - origin.x)
            selection.height = selection.y + abs(y - origin.y)
            
            selection.x = max( selection.x, 0 )
            selection.y = max( selection.y, 0 )
            selection.width = min( selection.width, image.width )
            selection.height = min( selection.height, image.height )
            selection.width -= selection.x
            selection.height -= selection.y

        if event == CV_EVENT_LBUTTONDOWN:
            origin = cvPoint(x,y)
            selection = cvRect(x,y,0,0)
            select_object = 1
        elif event == CV_EVENT_LBUTTONUP:
            select_object = 0
            if selection.width > 0 and selection.height > 0:
                track_object = -1


    def hsv2rgb(hue):
        rgb=[0,0,0]
        
        sector_data= ((0,2,1), (1,2,0), (1,0,2), (2,0,1), (2,1,0), (0,1,2))
        hue *= 0.033333333333333333333333333333333
        sector = cvFloor(hue)
        p = cvRound(255*(hue - sector))
        p ^= 255 if bool(sector & 1) else 0

        rgb[sector_data[sector][0]] = 255
        rgb[sector_data[sector][1]] = 0
        rgb[sector_data[sector][2]] = p

        return cvScalar(rgb[2], rgb[1], rgb[0], 0)

    def set_capture(self, cam):
        """
        Initialize the capture and sets the main settings.
        
        Arguments:
        - self: The main object pointer
        - cam: The camera device index. For Example: 0 = /dev/video0, 1 = /dev/video1
        """
        
        # Starts the Capture using the async method.
        # This means that self.cap.sync() wont be called periodically
        # by the idm because the Capture syncs the image asynchronously (See dev/camera.py)
        self.cap = Capture(async=True, idx=cam)
        
        # This sets the final image default color to rgb. The default color is bgr.
        self.cap.change(color="rgb")

    def get_image(self):
        """
        Gets the last queried and formated image.
        Function used by the mousetrap/ui/main.py 
        to get the output image

        Arguments:
        - self: The main object pointer

        returns self.cap.resize(200, 160, True)
        """

        # Calls the resize method passing the new with, height
        # specifying that the new image has to be a copy of the original
        # so, self.cap.resize will copy the original instead of modifying it.
        return self.cap.resize(200, 160, True)

    def get_pointer(self):
        """
        Returns the new MousePosition.
        Function used to pass the Mouse Pointer position
        to the Scripts.

        Arguments:
        - self: The main object pointer
        """

        # The return value has to be a Point() type object
        # Following the forehad IDM, The return is self.cap.forehead
        # which is created in the get_forehead function as an attribute
        # of self.cap
        return self.cap.pointer
