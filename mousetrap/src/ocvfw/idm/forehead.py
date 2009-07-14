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

import ocvfw.debug as debug
import ocvfw.commons as commons
from ocvfw.dev.camera import Capture, Point

a_name = "Forehead"
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

        debug.debug("ocvfw.idm", "Starting %s idm" % a_name)
        
        self.ctr          = controller
        self.cap          = None
        self.stgs         = stgs

        ##############################
        #  MOTION RELATED VARIABLES  #
        ##############################

        #self.step         = self.settings.getint( "mouse", "stepSpeed" )
        self.forehead     = None
        self.foreheadLast = None
        self.foreheadOrig = None
        self.foreheadDiff = None
        self.stopMove     = None
        self.startMove    = None

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
        
        self.cap = Capture(async=True, idx=cam, backend="OcvfwPython")
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

        if not hasattr(self.cap, "forehead"):
            self.get_forehead()

        #return self.cap.resize(200, 160, True)
        return self.cap

    def get_pointer(self):
        """
        Returns the new MousePosition

        Arguments:
        - self: The main object pointer
        """

        if hasattr(self.cap, "forehead"):
            return self.cap.forehead

    def get_forehead(self):
        eyes = False
        #self.cap.add_message("Getting Forehead!!!")

        face     = self.cap.get_area(commons.haar_cds['Face'])

        if face:
            areas    = [ (pt[1].x - pt[0].x)*(pt[1].y - pt[0].y) for pt in face ]
            startF   = face[areas.index(max(areas))][0]
            endF     = face[areas.index(max(areas))][1]

            # Shows the face rectangle
            #self.cap.add( Graphic("rect", "Face", ( startF.x, startF.y ), (endF.x, endF.y), parent=self.cap) )

            eyes = self.cap.get_area( commons.haar_cds['Eyes'], {"start" : startF.x,
                                                         "end" : startF.y,
                                                         "width" : endF.x - startF.x,
                                                         "height" : endF.y - startF.y}, (startF.x, startF.y) )

        if eyes:
            areas = [ (pt[1].x - pt[0].x)*(pt[1].y - pt[0].y) for pt in eyes ]

            point1, point2   = eyes[areas.index(max(areas))][0], eyes[areas.index(max(areas))][1]

            # Shows the eyes rectangle
            #self.cap.add(Graphic("rect", "Face", ( point1.x, point1.y ), (point2.x, point2.y), parent=self.cap))

            X, Y = ( (point1.x + point2.x) / 2 ), ( point1.y + ( (point1.y + point2.y) / 2 ) ) / 2
            self.cap.add( Point("point", "forehead", ( X, Y ), parent=self.cap, follow=True) )
            return True

        self.foreheadOrig = None

        return False
