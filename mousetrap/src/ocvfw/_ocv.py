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


try:
    from ctypesopencv import cv
    from ctypesopencv import highgui
except:
    print "This modules depends of opencv libraries"


class Ocvfw:
    """
    This Class controlls the main camera functions.
    It works as a little framework for OpenCV.
    """

    def __init__( self ):
        """
        Initialize the module and set its main variables.
        """

        self.img          = None
        self.mhi          = None
        self.img_lkpoints = { "current" : [],
                              "last"    : [],
                              "points"  : [] }
        self.imageScale   = 1.5

    def add_message(self, message, font=cv.CV_FONT_HERSHEY_COMPLEX, poss=None):
        """
        Write a message into the image.

        Arguments:
        - self: The main object pointer.
        - message: A string with the message.
        - font: An OpenCV font to use.
        - poss: The position of the message in the image. NOTE: Not enabled yet.
        """

        font = cv.cvInitFont ( font, 1, 1, 0.0, 1, cv.CV_AA)
        textSize, ymin = cv.cvGetTextSize (message, font)
        pt1 = cv.cvPoint ( ( self.img.width - textSize.width ) / 2 , 20 )
        cv.cvPutText (self.img, message, pt1, font, cv.cvScalar (255, 0, 0))

    def get_haar_points(self, haarCascade, method=cv.CV_HAAR_DO_CANNY_PRUNING):
        """
        Search for points matching the haarcascade selected.

        Arguments:
        - self: The main object pointer.
        - haarCascade: The selected cascade.
        - methode: The search method to use. DEFAULT: cv.CV_HAAR_DO_CANNY_PRUNING.

        Returns a list with the matches.
        """

        cascade = cv.cvLoadHaarClassifierCascade( haarCascade, self.imgSize )

        if not cascade:
            debug.exception( "ocvfw", "The Haar Classifier Cascade load failed" )

        cv.cvResize( self.img, self.small_img, cv.CV_INTER_LINEAR )

        cv.cvClearMemStorage( self.storage )

        points = cv.cvHaarDetectObjects( self.small_img, cascade, self.storage, 1.2, 2, method, cv.cvSize(20, 20) )

        if points:
            matches = [ [ cv.cvPoint( int(r.x*self.imageScale), int(r.y*self.imageScale)), \
                          cv.cvPoint( int((r.x+r.width)*self.imageScale), int((r.y+r.height)*self.imageScale) )] \
                          for r in points]
            debug.debug( "ocvfw", "cmGetHaarPoints: detected some matches" )
            return matches

    def get_haar_roi_points(self, haarCascade, rect, origSize=(0, 0), method=cv.CV_HAAR_DO_CANNY_PRUNING):
        """
        Search for points matching the haarcascade selected.

        Arguments:
        - self: The main object pointer.
        - haarCascade: The selected cascade.
        - methode: The search method to use. DEFAULT: cv.CV_HAAR_DO_CANNY_PRUNING.

        Returns a list with the matches.
        """

        cascade = cv.cvLoadHaarClassifierCascade( haarCascade, self.imgSize )

        if not cascade:
            debug.exception( "ocvfw", "The Haar Classifier Cascade load failed" )

        cv.cvClearMemStorage(self.storage)

        imageROI = cv.cvGetSubRect(self.img, rect)

        if cascade:
            points = cv.cvHaarDetectObjects( imageROI, cascade, self.storage,
                                    1.2, 2, method, cv.cvSize(20,20) )
        else:
            debug.exception( "ocvfw", "The Haar Classifier Cascade load Failed (ROI)" )

        if points:
            matches = [ [ cv.cvPoint( int(r.x+origSize[0]), int(r.y+origSize[1])), \
                          cv.cvPoint( int(r.x+r.width+origSize[0]), int(r.y+r.height+origSize[1] ))] \
                          for r in points]

            debug.debug( "ocvfw", "cmGetHaarROIPoints: detected some matches" )
            return matches

    def set_lkpoint(self, point):
        """
        Set a point to follow it using the L. Kallman method.

        Arguments:
        - self: The main object pointer.
        - point: A cv.cvPoint Point.
        """

        cvPoint = cv.cvPoint( point.x, point.y )

        self.img_lkpoints["current"] = [ cv.cvPointTo32f ( cvPoint ) ]

        if self.img_lkpoints["current"]:
            cv.cvFindCornerSubPix (
                self.grey,
                self.img_lkpoints["current"],
                cv.cvSize (20, 20), cv.cvSize (-1, -1),
                cv.cvTermCriteria (cv.CV_TERMCRIT_ITER | cv.CV_TERMCRIT_EPS, 20, 0.03))

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
        self.img_lkpoints["current"], status = cv.cvCalcOpticalFlowPyrLK (
            self.prevGrey, self.grey, self.prevPyramid, self.pyramid,
            self.img_lkpoints["last"], len( self.img_lkpoints["last"] ),
            cv.cvSize (20, 20), 3, len( self.img_lkpoints["last"] ), None,
            cv.cvTermCriteria (cv.CV_TERMCRIT_ITER|cv.CV_TERMCRIT_EPS, 20, 0.03), 0)

        # initializations
        counter = 0
        new_points = []

        for point in self.img_lkpoints["current"]:

            if not status[counter]:
                continue

            # this point is a correct point
            current = self.img_lkpoints["points"][counter]
            current.set_opencv(cv.cvPoint(int(point.x), int(point.y)))

            new_points.append( point )

            setattr(current.parent, current.label, current)

            # draw the current point
            current.parent.draw_point(point.x, point.y)

            # increment the counter
            counter += 1


        #debug.debug( "ocvfw", "cmShowLKPoints: Showing %d LK Points" % counter )

        # set back the self.imgPoints we keep
        self.img_lkpoints["current"] = new_points

    def wait_key(self, num):
        """
        Simple call to the highgui.cvWaitKey function, which has to be called periodically.

        Arguments:
        - self: The main object pointer.
        - num: An int value.
        """
        return highgui.cvWaitKey(num)

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

    def start_camera(self, idx, params = None):
        """
        Starts the camera capture using highgui.

        Arguments:
        - params: A list with the capture properties. NOTE: Not implemented yet.
        """
        self.capture = highgui.cvCreateCameraCapture( int(idx) )
        debug.debug( "ocvfw", "cmStartCamera: Camera Started" )

    def query_image(self, bgr=False, flip=False):
        """
        Queries the new frame.

        Arguments:
        - self: The main object pointer.
        - bgr: If True. The image will be converted from RGB to BGR.

        Returns The image even if it was stored in self.img
        """

        frame = highgui.cvQueryFrame( self.capture )

        if not  self.img:
            self.storage        = cv.cvCreateMemStorage(0)
            self.imgSize        = cv.cvGetSize (frame)
            self.img            = cv.cvCreateImage ( self.imgSize, 8, 3 )
            #self.img.origin     = frame.origin
            self.grey           = cv.cvCreateImage ( self.imgSize, 8, 1 )
            self.yCrCb          = cv.cvCreateImage ( self.imgSize, 8, 3 )
            self.prevGrey       = cv.cvCreateImage ( self.imgSize, 8, 1 )
            self.pyramid        = cv.cvCreateImage ( self.imgSize, 8, 1 )
            self.prevPyramid    = cv.cvCreateImage ( self.imgSize, 8, 1 )
            self.small_img       = cv.cvCreateImage( cv.cvSize( cv.cvRound ( self.imgSize.width/self.imageScale),
                                    cv.cvRound ( self.imgSize.height/self.imageScale) ), 8, 3 )
        self.img = frame
        cv.cvCvtColor(self.img, self.grey, cv.CV_BGR2GRAY)

        self.wait_key(10)
        return True


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
