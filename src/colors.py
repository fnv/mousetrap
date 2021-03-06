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
        image = None
        self.hsv = None
        self.hue = None
        self.mask = None
        self.backproject = None
        self.histimg = None
        self.hist = None

        self.backproject_mode = 0
        self.select_object = 0
        self.track_object = 0
        self.show_hist = 1
        self.origin = None
        self.selection = None
        self.track_window = None
        self.track_box = None
        self.track_comp = None
        self.hdims = 16

       # initial settings for value, saturation, and hue
        self.vmin = c_int(10)
        self.vmax = c_int(256)
        self.smin = c_int(80)
        self.smax = c_int(256)
        self.hmin = c_int(0)
        self.hmax = c_int(180) #this may have to be 180 and not 256, for whatever reason
        self.h2min = c_int(170)
        self.h2max = c_int(175)

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

 

    def on_mouse(self, event, x, y, flags, param):
        print str(event)
        #global select_object, selection, self.track_object, origin
    
        if self.cap.image() is None:
            return

        if self.origin:
            y = self.cap.image().height - y

        if self.select_object:
            self.selection.x = min(x,self.origin.x)
            self.selection.y = min(y,self.origin.y)
            self.selection.width = self.selection.x + abs(x - self.origin.x)
            self.selection.height = self.selection.y + abs(y - self.origin.y)
            
            self.selection.x = max( self.selection.x, 0 )
            self.selection.y = max( self.selection.y, 0 )
            self.selection.width = min( self.selection.width, self.cap.image().width )
            self.selection.height = min( self.selection.height, self.cap.image().height )
            self.selection.width -= self.selection.x
            self.selection.height -= self.selection.y

        if event == CV_EVENT_LBUTTONDOWN:
            self.origin = cvPoint(x,y)
            self.selection = cvRect(x,y,0,0)
            self.select_object = 1
        elif event == CV_EVENT_LBUTTONUP:
            self.select_object = 0
            if self.selection.width > 0 and self.selection.height > 0:
                self.track_object = -1


    def hsv2rgb(stupid, hue):
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

        """argc = len(argv)    
        if argc == 1 or (argc == 2 and argv[1].isdigit()):
            capture = cvCaptureFromCAM( int(argv[1]) if argc == 2 else 0 )
        elif argc == 2:
            capture = cvCaptureFromAVI( argv[1] )
        else:
            capture = None

        if not capture:
            print "Could not initialize capturing..."
            exit(-1)

        #HOTT KEYS!!!!1
        print "Hot keys: \n" \
            "\tESC - quit the program\n" \
            "\tc - stop the tracking\n" \
            "\tb - switch to/from backprojection view\n" \
            "\th - show/hide object histogram\n" \
            "To initialize tracking, select the object with mouse\n"

        #what windows do we want?"""
        cvNamedWindow( "Histogram", 1 )
        cvNamedWindow( "CamShiftDemo", 1 ) #main image
        cvNamedWindow( "Mask", 1 )
        #cvNamedWindow( "Backproject", 1)
        #cvNamedWindow( "Hue", 1)

        #enables mouse event monitoring in the main image window
        cvSetMouseCallback( "CamShiftDemo", self.on_mouse )

        cvCreateTrackbar( "Vmin", "CamShiftDemo", self.vmin, 256 )
        cvCreateTrackbar( "Vmax", "CamShiftDemo", self.vmax, 256 )
        cvCreateTrackbar( "Smin", "CamShiftDemo", self.smin, 256 )
        cvCreateTrackbar( "Smax", "CamShiftDemo", self.smax, 256 )

        #select the ranges of hues you want to track
        cvCreateTrackbar( "Hmin", "CamShiftDemo", self.hmin, 180 )
        cvCreateTrackbar( "Hmax", "CamShiftDemo", self.hmax, 180 )
        #cvCreateTrackbar( "H2min", "CamShiftDemo", h2min, 180 )
        #cvCreateTrackbar( "H2max", "CamShiftDemo", h2max, 180 )


        self.hue = cvCreateImage( cvSize(640,480), 8, 1 )
        self.mask = cvCreateImage( cvSize(640,480), 8, 1 )
        """mask2 = cvCreateImage( cvGetSize(frame), 8, 1 )
        maskcombo = cvCreateImage( cvGetSize(frame), 8, 1 )"""
        self.backproject = cvCreateImage( cvSize(640,480), 8, 1 )
        self.hist = cvCreateHist( [self.hdims], CV_HIST_ARRAY, [[0, 180]] )
        self.histimg = cvCreateImage( cvSize(320,200), 8, 3 )
        self.temp = cvCreateImage( cvSize(640, 480), 8, 3)
        cvZero( self.histimg )
        #loop
        while True:
            """#get next frame
            frame = cvQueryFrame( self.cap.image )
            if not frame:
                break

            if not image:
                # allocate all the buffers
                image = cvCreateImage( cvGetSize(frame), 8, 3 )
                image.origin = frame.origin
                hsv = cvCreateImage( cvGetSize(frame), 8, 3 )"""

            
            self.cap.sync()
            #cvCopy(frame, image)
            self.hsv = self.cap.color("hsv", channel=3, copy=True) #make the image hsv
            self.cap.color("bgr", channel=3, copy=True)
            #cvCvtColor( self.cap.image, self.hsv, CV_BGR2HSV )
            #self.track_object=-1
            #print "ABOUT TO GOT IN"
            if self.track_object != 0:
                #print "UNEQUAL" + str(self.track_object)
                #updates the hsv values to be masked
                #self.hsv = cvGetImage( self.hsv, self.temp );
                scalar1=cvScalar(self.hmin.value,self.smin.value,min(self.vmin.value,self.vmax.value),0)
                scalar2=cvScalar(self.hmax.value,self.smax.value,max(self.vmin.value,self.vmax.value),0)
                cvInRangeS( (self.hsv), scalar1, scalar2, self.mask )
                #cvInRangeS( self.hsv, cvScalar(h2min.value,smin.value,min(vmin.value,vmax.value),0),
                #                cvScalar(h2max.value,smax.value,max(vmin.value,vmax.value),0), mask2 )
                cvSplit(self.hsv, self.hue) #extract hue information?

                #cvOr(mask, mask2, maskcombo) #combine the masks so that EITHER color is accepted
                #selection=cvRect(10,10,20,20)
                if self.track_object < 0: #OH OKAY negative means it's tracking so... make a histogram     
                    #print "LESS" + str(self.track_object)
                    cvSetImageROI( self.hue, self.selection )
                    cvSetImageROI( self.mask, self.selection )
                    cvCalcHist( [self.hue], self.hist, 0, self.mask );
                    min_val, max_val = cvGetMinMaxHistValue(self.hist)
                    hbins = self.hist.bins[0]
                    cvConvertScale( hbins, hbins, 255. / max_val if max_val else 0., 0 )
                    cvResetImageROI( self.hue ) # ^ hisogram stuff, v tracking stuff
                    cvResetImageROI( self.mask )
                    self.track_window = self.selection #the original window to track is your mouse selection
                    self.track_object = 1 #now objects are being tracked

                    #more histogram stuff -- now we're displaying it
                    cvZero( self.histimg )
                    bin_w = self.histimg.width / self.hdims
                    for i in xrange(self.hdims):
                        val = cvRound( cvGetReal1D(hbins,i)*self.histimg.height/255 )
                        color = self.hsv2rgb(i*180./self.hdims)                        cvRectangle( self.histimg, cvPoint(i*bin_w,self.histimg.height),
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
                    cvCvtColor( self.backproject, self.cap.image(), CV_GRAY2BGR ) #why??
                if not self.origin:
                    self.track_box.angle = -self.track_box.angle #why??"""
                # Make sure its a number.
                if math.isnan(self.track_box.size.height): 
                    self.track_box.size.height = 0
                if math.isnan(self.track_box.size.width): 
                    self.track_box.size.width = 0
                #draws an ellipse around it. the ellipse is GREEN!!!!
                cvEllipseBox( self.cap.image(), self.track_box, CV_RGB(0,255,0), 3, CV_AA, 0 )
                
                #still lost
            if bool(self.select_object) and self.selection.width > 0 and self.selection.height > 0:
                cvSetImageROI( self.cap.image(), self.selection )
                cvXorS( self.cap.image(), cvScalarAll(255), self.cap.image() )
                cvResetImageROI( self.cap.image() )

            #hey let's show some stuff in those empty windows!!"""
            cvShowImage( "CamShiftDemo", self.cap.image() )
            cvShowImage( "Histogram", self.histimg )
            cvShowImage( "Mask", self.mask )
            #cvShowImage( "Backproject", backproject)
            #cvShowImage( "Hue", hue)

            #HOTT KEYS!!!!1
            """c = '%c' % (cvWaitKey(10) & 255)
            if c == '\x1b':
                break
            elif c == 'b':
                backproject_mode ^= 1
            elif c =='c':
                self.track_object = 0
                cvZero( histimg )
            elif c =='h':
                show_hist ^= 1
                if not show_hist:
                    cvDestroyWindow( "Histogram" )
                else:
                    cvNamedWindow( "Histogram", 1 )
        print "Hoiahdfoiahs"
        return image
        # Calls the resize method passing the new with, height
        # specifying that the new image has to be a copy of the original
        # so, self.cap.resize will copy the original instead of modifying it."""
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
        self.cap.pointer=Point("point", "color", ( 1, 2 ), parent=self.cap, follow=True) 
        return self.cap.pointer
