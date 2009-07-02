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


"""Forehead IDM"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import ocvfw.commons as commons
from ocvfw.dev.camera import Camera, Capture, Point

# IDM's Information
# a_name: IDM's name
#   This is used by the settings gui to identify the idm
# a_description: IDM's Description
# a_settings: Possible settings needed by the idm. For Example: { 'var_name' : { 'value' : default_value}, 'var_name2' : { 'value' : default_value} }
a_name = "IDM Name"
a_description = "Forehead point tracker based on LK Algorithm"
a_settings = { 'speed' : {"value":2}}

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
