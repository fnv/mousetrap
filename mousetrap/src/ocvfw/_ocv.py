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

"""Little  Framework for OpenCV Library."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import time
import debug
import commons as co

class OcvfwBase:

    def __init__( self ):
        """
        Initialize the module and set its main variables.
        """

        self.img          = None
        self.mhi          = None
        self.img_lkpoints = { "current" : [],
                              "last"    : [],
                              "points"  : [] }

        self.__lk_swap = False
        self.imageScale   = 1.5

    def set(self, key, value):
        """
        """
        if hasattr(self, "%s" % key):
            getattr(self, "%s" % key)(value)
            debug.debug("OcvfwBase", "Changed %s value to %s" % (key, value))
            return True
        
        debug.debug("OcvfwBase", "%s not found" % (key))
        return False

    def lk_swap(self, set=None):
        """
        Enables/Disable the lk points swapping action.

        Arguments:
        - self: The main object pointer.
        - set: The new value. If None returns the current state.
        """
        
        if set is None:
            return self.__lk_swap
        
        self.__lk_swap = set

    def new_image(self, size, num, ch):
        """
        Creates a new image 
        """

        if type(size) == "<type 'tuple'>":
            size = co.cv.cvSize( size[0], size[1])

        return co.cv.cvCreateImage( size, num, ch)

    def set_camera_idx(self, idx):
        """
        Changes the camera device index.

        Arguments:
        - self: The main object pointer.
        - idx: The camera index. For Example: 0 for /dev/video0
        """
        self.idx = idx

    def wait_key(self, num):
        """
        Simple call to the highgui.cvWaitKey function, which has to be called periodically.

        Arguments:
        - self: The main object pointer.
        - num: An int value.
        """
        return co.hg.cvWaitKey(num)

    def start_camera(self, params = None):
        """
        Starts the camera capture using highgui.

        Arguments:
        - params: A list with the capture properties. NOTE: Not implemented yet.
        """
        self.capture = co.hg.cvCreateCameraCapture( int(self.idx) )
        debug.debug( "ocvfw", "cmStartCamera: Camera Started" )

    def query_image(self, bgr=False, flip=False):
        """
        Queries the new frame.

        Arguments:
        - self: The main object pointer.
        - bgr: If True. The image will be converted from RGB to BGR.

        Returns The image even if it was stored in self.img
        """

        frame = co.hg.cvQueryFrame( self.capture )

        if not  self.img:
            self.storage        = co.cv.cvCreateMemStorage(0)
            self.imgSize        = co.cv.cvGetSize (frame)
            self.img            = co.cv.cvCreateImage ( self.imgSize, 8, 3 ) #16?
            #self.img.origin     = frame.origin
            self.grey           = co.cv.cvCreateImage ( self.imgSize, 8, 1 )
            self.yCrCb          = co.cv.cvCreateImage ( self.imgSize, 8, 3 )
            self.prevGrey       = co.cv.cvCreateImage ( self.imgSize, 8, 1 )
            self.pyramid        = co.cv.cvCreateImage ( self.imgSize, 8, 1 )
            self.prevPyramid    = co.cv.cvCreateImage ( self.imgSize, 8, 1 )
            self.small_img       = co.cv.cvCreateImage( co.cv.cvSize( co.cv.cvRound ( self.imgSize.width/self.imageScale),
                                    co.cv.cvRound ( self.imgSize.height/self.imageScale) ), 8, 3 )
        self.img = frame
        co.cv.cvCvtColor(self.img, self.grey, co.cv.CV_BGR2GRAY)

        self.wait_key(10)
        return True

    def set_lkpoint(self, point):
        """
        Set a point to follow it using the L. Kallman method.

        Arguments:
        - self: The main object pointer.
        - point: A co.cv.cvPoint Point.
        """

        cvPoint = co.cv.cvPoint( point.x, point.y )

        self.img_lkpoints["current"] = [ co.cv.cvPointTo32f ( cvPoint ) ]

        if self.img_lkpoints["current"]:
            co.cv.cvFindCornerSubPix (
                self.grey,
                self.img_lkpoints["current"],
                co.cv.cvSize (20, 20), co.cv.cvSize (-1, -1),
                co.cv.cvTermCriteria (co.cv.CV_TERMCRIT_ITER | co.cv.CV_TERMCRIT_EPS, 20, 0.03))

            point.set_opencv( cvPoint )
            self.img_lkpoints["points"].append(point)

            setattr(point.parent, point.label, point)

            if len(self.img_lkpoints["last"]) > 0:
                self.img_lkpoints["last"].append( self.img_lkpoints["current"][0] )

            debug.debug( "ocvfw", "cmSetLKPoints: New LK Point Added" )
        else:
            self.img_lkpoints["current"] = []

    def clean_lkpoints(self):
        """
        Cleans all the registered points.

        Arguments:
        - self: The main object pointer
        """

        self.img_lkpoints = { "current" : [],
                              "last"    : [],
                              "points"  : [] }

    def show_lkpoints(self):
        """
        Callculate the optical flow of the set points and draw them in the image.

        Arguments:
        - self: The main object pointer.
        """

        # calculate the optical flow
        self.img_lkpoints["current"], status = co.cv.cvCalcOpticalFlowPyrLK (
            self.prevGrey, self.grey, self.prevPyramid, self.pyramid,
            self.img_lkpoints["last"], len( self.img_lkpoints["last"] ),
            co.cv.cvSize (20, 20), 3, len( self.img_lkpoints["last"] ), None,
            co.cv.cvTermCriteria (co.cv.CV_TERMCRIT_ITER|co.cv.CV_TERMCRIT_EPS, 20, 0.03), 0)

        # initializations
        counter = 0
        new_points = []

        for point in self.img_lkpoints["current"]:

            if not status[counter]:
                continue

            # this point is a correct point
            current = self.img_lkpoints["points"][counter]
            current.set_opencv(co.cv.cvPoint(int(point.x), int(point.y)))

            new_points.append( point )

            setattr(current.parent, current.label, current)

            # draw the current point
            current.parent.draw_point(point.x, point.y)

            # increment the counter
            counter += 1


        #debug.debug( "ocvfw", "cmShowLKPoints: Showing %d LK Points" % counter )

        # set back the self.imgPoints we keep
        self.img_lkpoints["current"] = new_points


    def swap_lkpoints(self):
        """
        Swap the LK method variables so the new points will be the last points.
        This function has to be called after showing the new points.

        Arguments:
        - self: The main object pointer.
        """

        # swapping
        self.prevGrey, self.grey               = self.grey, self.prevGrey
        self.prevPyramid, self.pyramid         = self.pyramid, self.prevPyramid
        self.img_lkpoints["last"], self.img_lkpoints["current"] = \
                                   self.img_lkpoints["current"], self.img_lkpoints["last"]


class OcvfwCtypes(OcvfwBase):
    """
    This Class controlls the main camera functions.
    It works as a little framework for Openco.cv.

    This Backend uses ctypes opencv python bindings.
    """
    

    def __init__(self):
        """
        Initialize the module and set its main variables.
        """
        co.cv = __import__("ctypesopencv.cv",
                        globals(),
                        locals(),
                        [''])
        
        co.hg = __import__("ctypesopencv.highgui",
                        globals(),
                        locals(),
                        [''])
 
        OcvfwBase.__init__(self)


class OcvfwPython(OcvfwBase):
    """
    This Class controlls the main camera functions.
    It works as a little framework for Openco.cv.

    This Backend uses normal opencv python bindings.
    """

    co.cv = __import__("opencv.cv",
                        globals(),
                        locals(),
                        [''])
        
    co.hg = __import__("opencv.highgui",
                        globals(),
                        locals(),
                        [''])

    def __init__( self ):
        """
        Initialize the module and set its main variables.
        """

        OcvfwBase.__init__(self)

    def add_message(self, message, font=co.cv.CV_FONT_HERSHEY_COMPLEX, poss=None):
        """
        Write a message into the image.

        Arguments:
        - self: The main object pointer.
        - message: A string with the message.
        - font: An OpenCV font to use.
        - poss: The position of the message in the image. NOTE: Not enabled yet.
        """

        font = co.cv.cvInitFont ( font, 1, 1, 0.0, 1, co.cv.CV_AA)
        textSize, ymin = co.cv.cvGetTextSize (message, font)
        pt1 = co.cv.cvPoint ( ( self.img.width - textSize.width ) / 2 , 20 )
        co.cv.cvPutText (self.img, message, pt1, font, co.cv.cvScalar (255, 0, 0))

    def get_haar_points(self, haarCascade, method=co.cv.CV_HAAR_DO_CANNY_PRUNING):
        """
        Search for points matching the haarcascade selected.

        Arguments:
        - self: The main object pointer.
        - haarCascade: The selected cascade.
        - methode: The search method to use. DEFAULT: co.cv.CV_HAAR_DO_CANNY_PRUNING.

        Returns a list with the matches.
        """

        cascade = co.cv.cvLoadHaarClassifierCascade( haarCascade, self.imgSize )

        if not cascade:
            debug.exception( "ocvfw", "The Haar Classifier Cascade load failed" )

        co.cv.cvResize( self.img, self.small_img, co.cv.CV_INTER_LINEAR )

        co.cv.cvClearMemStorage( self.storage )

        points = co.cv.cvHaarDetectObjects( self.small_img, cascade, self.storage, 1.2, 2, method, co.cv.cvSize(20, 20) )

        if points:
            matches = [ [ co.cv.cvPoint( int(r.x*self.imageScale), int(r.y*self.imageScale)), \
                          co.cv.cvPoint( int((r.x+r.width)*self.imageScale), int((r.y+r.height)*self.imageScale) )] \
                          for r in points]
            debug.debug( "ocvfw", "cmGetHaarPoints: detected some matches" )
            return matches

    def get_haar_roi_points(self, haarCascade, rect, origSize=(0, 0), method=co.cv.CV_HAAR_DO_CANNY_PRUNING):
        """
        Search for points matching the haarcascade selected.

        Arguments:
        - self: The main object pointer.
        - haarCascade: The selected cascade.
        - methode: The search method to use. DEFAULT: co.cv.CV_HAAR_DO_CANNY_PRUNING.

        Returns a list with the matches.
        """

        cascade = co.cv.cvLoadHaarClassifierCascade( haarCascade, self.imgSize )

        if not cascade:
            debug.exception( "ocvfw", "The Haar Classifier Cascade load failed" )

        co.cv.cvClearMemStorage(self.storage)

        imageROI = co.cv.cvGetSubRect(self.img, rect)

        if cascade:
            points = co.cv.cvHaarDetectObjects( imageROI, cascade, self.storage,
                                    1.2, 2, method, co.cv.cvSize(20,20) )
        else:
            debug.exception( "ocvfw", "The Haar Classifier Cascade load Failed (ROI)" )

        if points:
            matches = [ [ co.cv.cvPoint( int(r.x+origSize[0]), int(r.y+origSize[1])), \
                          co.cv.cvPoint( int(r.x+r.width+origSize[0]), int(r.y+r.height+origSize[1] ))] \
                          for r in points]

            debug.debug( "ocvfw", "cmGetHaarROIPoints: detected some matches" )
            return matches

    ##########################################
    #                                        #
    #          THIS IS NOT USED YET          #
    #                                        #
    ##########################################
    def get_motion_points(self, imgRoi=None):
        """
        Calculate the motion points in the image.

        Arguments:
        - self: The main object pointer.
        - start: The start ROI point.
        - end: The end ROI point.
        - num: The nomber of points to return

        Returns A list with the points found.
        """

        mv = []
        n_ = 4

        timestamp = time.clock()/1.0

        if imgRoi:
            img     = cv.cvGetSubRect( self.img, imgRoi )
            imgSize = cv.cvSize( imgRoi.width, imgRoi.height )
            self.imgRoi = img
        else:
            img     = self.img
            imgSize = self.imgSize

        # Motion Related Variables
        if not self.mhi or self.mhi.width != imgSize.width or self.mhi.height != imgSize.height:
            self.buf        = [ 0, 0, 0, 0 ]
            self.lastFm     = 0
            self.mhiD       = 1
            self.maxTD      = 0.5
            self.minTD      = 0.05
            self.mask       = cv.cvCreateImage( imgSize,  8, 1 )
            self.mhi        = cv.cvCreateImage( imgSize, 32, 1 )
            self.orient     = cv.cvCreateImage( imgSize, 32, 1 )
            self.segmask    = cv.cvCreateImage( imgSize, 32, 1 )

            cv.cvZero( self.mhi )

            for i in range( n_ ):
                self.buf[i] = cv.cvCreateImage( imgSize, 8, 1 )
                cv.cvZero( self.buf[i] )

        idx1 = self.lastFm

        # convert frame to grayscale
        cv.cvCvtColor( img, self.buf[self.lastFm], cv.CV_BGR2GRAY )

        # index of (self.lastFm - (n_-1))th frame
        idx2 = ( self.lastFm + 1 ) % n_
        self.lastFm = idx2

        silh = self.buf[idx2]

        # Get difference between frames
        cv.cvAbsDiff( self.buf[idx1], self.buf[idx2], silh )

        # Threshold it
        cv.cvThreshold( silh, silh, 30, 1, cv.CV_THRESH_BINARY )

        # Update MHI
        cv.cvUpdateMotionHistory( silh, self.mhi, timestamp, self.mhiD )

        cv.cvCvtScale( self.mhi, self.mask, 255./self.mhiD, (self.mhiD - timestamp)*255./self.mhiD )

        cv.cvCalcMotionGradient( self.mhi, self.mask, self.orient, self.maxTD, self.minTD, 3 )

        cv.cvClearMemStorage( self.storage )

        seq = cv.cvSegmentMotion( self.mhi, self.segmask, self.storage, timestamp, self.maxTD )

        for i in range(0, seq.total):
            if i < 0:  # case of the whole image
                continue
            else:  # i-th motion component
                # Movement Rectangle
                mRect = seq[i].rect

                # reject very small components
                if( mRect.width + mRect.height < 30 ):
                    continue

            center = cv.cvPoint( (mRect.x + mRect.width/2), (mRect.y + mRect.height/2) )

            silhRoi = cv.cvGetSubRect(silh, mRect)
            count = cv.cvNorm( silhRoi, None, cv.CV_L1, None )

             # calculate number of points within silhouette ROI
            if( count < mRect.width * mRect.height * 0.05 ):
                continue

            mv.append(center)

        return mv
