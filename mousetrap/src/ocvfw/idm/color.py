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


"""Color IDM"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import ocvfw.commons as commons
from ocvfw.dev.camera import Camera, Capture, Point

from ctypes import c_int 
""" Using ctypes-opencv, instead of the python bindings provided by OpenCV. """
from ctypesopencv import *

from sys import argv, exit
import math

# IDM's Information
# a_name: IDM's name
#   This is used by the settings gui to identify the idm
# a_description: IDM's Description
# a_settings: Possible settings needed by the idm. For Example: { 'var_name' : { 'value' : default_value}, 'var_name2' : { 'value' : default_value} }  These settings are loaded from usrSettings.cfg in /home/username/.mousetrap.
a_name = "color"
a_description = "Color tracker using CAMshift algorithm"
a_settings = {"hrange": {"value": 15}, "vscale": {"value": 10}, "selection_size": {"value": 30}}

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
        
        self.cfg = self.ctr.cfg

        if not self.cfg.has_section("color"):
            self.cfg.add_section("color")
        # Capture instance
        # The capture is the object containing the image 
        # and all the possible methods to modify it.
        self.cap          = None
        
        # IDM's Settings dict
        self.stgs         = stgs

        # Prepares the IDM using the settings.
        self.prepare_config()

        #TODO: ADD CONDITIONAL TO ENSURE SETTINGS ARE SET EVEN IF YOU HAVE AN OLD CONFIG FILE

        # Initialization of variables needed for color tracking CAMshift algorithm.

        self.image = None
        self.hsv = None

        self.first_time=True # To keep track of whether or not we have initalized image objects

        self.backproject_mode = 0 #needed?
        self.select_object = 0
        self.track_object = 0
        self.show_hist = 1 #needed?
        self.origin = None #needed?
        self.selection = None
        self.track_window = None
        self.track_box = None
        self.track_comp = None
        self.hdims = 16

        # Variables to control the ranges for the color mask.
        self.vmin = c_int(10)   # Value
        self.vmax = c_int(256)
        self.smin = c_int(80)   # Saturation
        self.smax = c_int(256)
        self.hmin = c_int(0)    # Hue
        self.hmax = c_int(180)  # out of 180, not 256
        self.h2min = c_int(170)
        self.h2max = c_int(175)

        cvNamedWindow( "Histogram", 1 )
        cvNamedWindow( "Mask", 1 )

        cvCreateTrackbar( "Vmin", "Mask", self.vmin, 256 )
        cvCreateTrackbar( "Vmax", "Mask", self.vmax, 256 )
        cvCreateTrackbar( "Smin", "Mask", self.smin, 256 )
        cvCreateTrackbar( "Smax", "Mask", self.smax, 256 )
        cvCreateTrackbar( "Hmin", "Mask", self.hmin, 180 )
        cvCreateTrackbar( "Hmax", "Mask", self.hmax, 180 )



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

    def hsv2rgb(self, hue):
        """
        Converts an HSV hue to RGB.
        
        Arguments:
        - self: The main object pointer
        - hue: the hue to convert to RGB.
        """
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
        self.cap = Capture(async=False, idx=cam)
        
        # This sets the final image default color to rgb. The default color is bgr.
        self.cap.change(color="rgb")

    def _convertColorDepth(self, color):
        """
        Converts from 16 to 8 bit color depth. Necessary
        for OpenCV functions and GDK colors to interact as the
        former expects colors from 0-255 and the latter expects
        0-65535.
        
        Arguments:
        - self: The main object pointer
        - color: The integer color value to convert to 0-255
        """
        return int((color / 65535.0) * 255)

    def rgb2hue(self, red, green, blue):
        """
        Converts the rgb values from the config file into the corresponding hue value.
        This method was stolen from the gtk source!
        """

        hue = 0.0
          
        if (red > green):
            if (red > blue):
                cmax = red
            else:
                cmax = blue
            
            if (green < blue):
                cmin = green
            else:
                cmin = blue;
        else:
            if (green > blue):
                cmax = green
            else:
                cmax = blue
           
            if (red < blue):
                cmin = red
            else:
                cmin = blue
        
        val = cmax
        
        if (cmax != 0.0):
            sat = (cmax - cmin) / cmax
        else:
            sat = 0.0
        
        if (sat == 0.0):
            hue = 0.0
        else:
            delta = cmax - cmin
            
            if (red == cmax):
                hue = (green - blue) / delta
            elif (green == cmax):
                hue = 2 + (blue - red) / delta
            elif (blue == cmax):
                hue = 4 + (red - green) / delta
            
            hue /= 6.0;
            
            if (hue < 0.0):
                hue += 1.0
            elif (hue > 1.0):
                hue -= 1.0

        return (hue * 360) / 2

    def update_hue_range(self, *args):
        """
        WARNING: HACK by Ryan
        This method is used as a callback connected to the color picker
        save button's click event. I had to do this because we need to update
        the hue min/max in this idm whenever the user saves a new color.
        However, we can't poll a file's status to see if it's changed, so
        we routed the event to two callbacks.
        
        Suggestion: Maybe use a dictionary for configure settings and
        serialize it on quit. This would trivialize querying a settings
        structure and allow us comparatively free use of the data. Right now
        we're forced to keep in mind how often we query settings because
        hard drives are SLOW.
        """

        temphue = self.rgb2hue(float(self.cfg.get("color", "red")), float(self.cfg.get("color", "green")), float(self.cfg.get("color", "blue")))

        hrange = self.cfg.hrange / 2
        self.hmin.value = int(max(temphue - hrange, 0))
        self.hmax.value = int(min(temphue + hrange, 180))

    def get_image(self):
        """
        Gets the last queried and formated image.
        Function used by the mousetrap/ui/main.py 
        to get the output image

        Arguments:
        - self: The main object pointer

        returns self.cap.resize(200, 160, True)
        """
        # Needed to sync image in Mousetrap with camera frame?
        self.cap.sync()

        #self.image = self.cap.image().origin needed??
        self.image = self.cap.image()

        # Initialization of images.  Only needs to happen once.
        if self.first_time:
            # TODO: What is a better way to get the image size?
            self.hue = cvCreateImage( cvGetSize(self.image), 8, 1 )
            self.mask = cvCreateImage(  cvGetSize(self.image), 8, 1 )
            self.backproject = cvCreateImage(  cvGetSize(self.image), 8, 1 )
            self.hist = cvCreateHist( [self.hdims], CV_HIST_ARRAY, [[0, 180]] )
            self.histimg = cvCreateImage( cvSize(320,200), 8, 3 )
            self.temp = cvCreateImage(  cvGetSize(self.image), 8, 3) #needed?
            cvZero( self.histimg )

            temphue = self.rgb2hue(float(self.cfg.get("color", "red")), float(self.cfg.get("color", "green")), float(self.cfg.get("color", "blue")))

            hrange = self.cfg.hrange / 2
            self.hmin.value = int(max(temphue - hrange, 0))
            self.hmax.value = int(min(temphue + hrange, 180))
            print str(self.hmin.value) + ", " + str(self.hmax.value)


            #creates a woobly selection box one should put one's object in before tracking
            self.origin = cvPoint(self.image.width / 2, self.image.height / 2)
            self.selection = cvRect(self.origin.x-50,self.origin.y-50,100,100)

            self.first_time=False

        self.hsv = self.cap.color("hsv", channel=3, copy=True) # Convert to HSV

        # If a selection has been made or if an object is already being tracked:
        if self.track_object != 0:
            # Set up some scalars using the min/max values for hue, saturation, and value
            scalar1=cvScalar(self.hmin.value,self.smin.value,min(self.vmin.value,self.vmax.value),0)
            scalar2=cvScalar(self.hmax.value,self.smax.value,max(self.vmin.value,self.vmax.value),0)
            # Create a mask using the scalars            
            cvInRangeS( self.hsv, scalar1, scalar2, self.mask )

            cvSplit(self.hsv, self.hue)
            # If a selection has just been made and objects are not yet being tracked:
            if self.track_object < 0:
                # Set the range of interest for the hue and mask images
                cvSetImageROI( self.hue, self.selection) 
                cvSetImageROI( self.mask, self.selection)
                cvCalcHist( [self.hue], self.hist, 0, self.mask )
                min_val, max_val = cvGetMinMaxHistValue(self.hist)
                hbins = self.hist.bins[0]
                cvConvertScale( hbins, hbins, 255. / max_val if max_val else 0., 0 )
                cvResetImageROI( self.hue ) # ^ hisogram stuff, v tracking stuff
                cvResetImageROI( self.mask )
                self.track_window = self.selection # the original window to track is your mouse selection
                self.track_object = 1 # now objects are being tracked

                #more histogram stuff -- now we're displaying it
                cvZero( self.histimg )
                bin_w = self.histimg.width / self.hdims
                for i in xrange(self.hdims):
                    val = cvRound( cvGetReal1D(hbins,i)*self.histimg.height/255 )
                    color = self.hsv2rgb(i*180./self.hdims)                    cvRectangle( self.histimg, cvPoint(i*bin_w,self.histimg.height),
                                     cvPoint((i+1)*bin_w,self.histimg.height - val),
                                     color, -1, 8, 0 )
            #calculate the back projection (dunno what this is)
            cvCalcBackProject( [self.hue], self.backproject, self.hist )
            #mask the backprojection (why? who knows)
            cvAnd(self.backproject, self.mask, self.backproject)
            #CAMSHIFT HAPPENS
            niter, self.track_comp, self.track_box = cvCamShift( self.backproject, self.track_window,
                        cvTermCriteria( CV_TERMCRIT_EPS | CV_TERMCRIT_ITER, 10, 1 ))
            self.track_window = self.track_comp.rect #no idea
            
            if self.backproject_mode:
                cvCvtColor( self.backproject, self.image, CV_GRAY2BGR ) #why??
            if not self.origin:
                self.track_box.angle = -self.track_box.angle #why??"""
            # Make sure it's a number.
            if math.isnan(self.track_box.size.height): 
                self.track_box.size.height = 0
            if math.isnan(self.track_box.size.width): 
                self.track_box.size.width = 0
            #draws an ellipse around it. the ellipse is GREEN!!!! sometimes
            cvEllipseBox( self.image, self.track_box, CV_RGB(0,255,0), 3, CV_AA, 0 )

            if (not hasattr(self.cap, "obj_center")):
                self.cap.add(Point("point", "obj_center", ( int(self.track_box.center.x), int(self.track_box.center.y )), parent=self.cap, follow=True))
            else:
                self.cap.obj_center.set_opencv(cvPoint(int(self.track_box.center.x), int(self.track_box.center.y)))

            #this displays the selection box before tracking starts
        if not self.track_object:
            cvSetImageROI( self.image, self.selection )
            cvXorS( self.image, cvScalarAll(255), self.image )
            cvResetImageROI( self.image )



        #hey let's show some stuff in those empty windows!!"""
        cvShowImage( "Histogram", self.histimg )
        cvShowImage( "Mask", self.mask)
        
        self.cap.color("rgb", channel=3, copy=True)

        #Press t to start tracking! Press x to stop tracking!
        c = '%c' % (cvWaitKey(10) & 255)
        if c == 't':
            if self.selection.width > 0 and self.selection.height > 0:
                self.track_object = -1
        if c == 'x':
            #self.cap.remove("obj_center")
            self.track_object = 0

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
        # Following the forehad IDM, The return is self.cap.obj_center
        # which is created in the get_image function as an attribute
        # of self.cap

        if hasattr(self.cap, "obj_center"):
            return self.cap.obj_center
        else:
            pass


