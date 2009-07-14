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

import pyvision as pv
import ocvfw.debug as debug
import ocvfw.commons as commons
from ocvfw.dev.camera import Capture, Point
from pyvision.face.FilterEyeLocator import loadFilterEyeLocator as eye_locator

from opencv import cv

a_name = "Eyes"
a_description = "Eyes point tracker using pyvision"
a_settings = { }

FEL_NAME = "/home/flaper87/MouseTrap/src/ocvfw/idm/EyeLocatorASEF128x128.fel"

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
        debug.debug("ocvfw.idm", "Starting %s idm" % a_name)
        
        self.img          = None
        self.ctr          = controller
        self.cap          = None
        self.stgs         = stgs

        ##############################
        #  MOTION RELATED VARIABLES  #
        ##############################

        self.fel = eye_locator(FEL_NAME)

        ##############################
        #       ACTION POINTS        #
        ##############################
        self.mpPointer       = None

        ##############################
        #  CLICK RELATED VARIABLES   #
        ##############################

        self.isMoving       = False

        self.prepare_config()
        debug.info("ocvfw.idm", "Forhead Algorithm loaded")

    def prepare_config(self):
        """
        Prepares the IDM using the settings

        Arguments:
        - self: The main object pointer
        """
        global a_settings

        for key in self.stgs:
            pass

    def set_capture(self, cam):
        """
        Initialize the capture and sets the main settings.

        Arguments:
        - self: The main object pointer
        - cam: The camera device index. For Example: 0 = /dev/video0, 1 = /dev/video1
        """
        
        debug.debug("ocvfw.idm", "Setting Capture")
        
        self.cap = Capture(async=False, idx=cam, backend="OcvfwPython")
        self.cap.change(color="rgb")
        self.cap.set_camera("lk_swap", True)

    def calc_motion(self):
        if not hasattr(self.cap, "forehead"):
            self.get_forehead()

    def get_capture(self):
        """
        Sets the forehead point if needed and returns the formated image.

        Arguments:
        - self: The main object pointer

        returns self.cap.image()
        """
        self.cap.sync()
        if not hasattr(self.cap, "leye") or not hasattr(self.cap, "reye"):
            self.get_eye()
            
        return self.cap

    def get_pointer(self):
        """
        Returns the new MousePosition

        Arguments:
        - self: The main object pointer
        """

        return True

    def get_eye(self):
        eyes = False

        face     = self.cap.get_area(commons.haar_cds['Face'])

        if face:
            cvtile = cv.cvCreateMat(128,128,cv.CV_8UC3)
            bwtile = cv.cvCreateMat(128,128,cv.CV_8U)
            areas    = [ (pt[1].x - pt[0].x)*(pt[1].y - pt[0].y) for pt in face ]
            startF   = face[areas.index(max(areas))][0]
            endF     = face[areas.index(max(areas))][1]
            facerect     = self.cap.rect(startF.x, startF.y, endF.x - startF.x, endF.y - startF.y)

            if not facerect:
                return

            cv.cvResize(facerect, cvtile)

            cv.cvCvtColor( cvtile, bwtile, cv.CV_BGR2GRAY )

            leye,reye,lcp,rcp = self.fel.locateEyes(bwtile)
            leye = pv.Point(leye)
            reye = pv.Point(reye)

            leye_x = int((float(leye.X())*facerect.width/cvtile.width) + startF.x)
            leye_y = int((float(leye.Y())*facerect.height/cvtile.height) + startF.y)

            reye_x = int((float(reye.X())*facerect.width/cvtile.width) + startF.x)
            reye_y = int((float(reye.Y())*facerect.height/cvtile.height) + startF.y)

            eye_rect = { "startX" : leye_x - 5,
                         "startY" : leye_y - 5,
                         "endX"   : leye_x + 5,
                         "endY"   : leye_y + 5}

            #self.cap.image(self.cap.rect(leye_x - 5, leye_y - 5, 20, 20))

            if not hasattr(self.cap, "leye"):
                self.cap.add( Point("point", "leye", [int(leye_x), int(leye_y)], parent=self.cap, follow=True) )
            else:
                self.cap.add( Point("point", "reye", [int(reye_x), int(reye_y)], parent=self.cap, follow=True) )

            # Shows the face rectangle
            #self.cap.add( Graphic("rect", "Face", ( startF.x, startF.y ), (endF.x, endF.y), parent=self.cap) )


        self.foreheadOrig = None

        return False
