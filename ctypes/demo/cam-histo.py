#!/usr/bin/env python
# OpenCV's Python demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv

import sys

# import the necessary things for OpenCV
from opencv import *

#############################################################################
# definition of some constants

# how many bins we want for the histogram, and their ranges
hdims = 16
hranges = [[0, 180]]

# ranges for the limitation of the histogram
vmin = 10
vmax = 256
smin = 30

# the range we want to monitor
hsv_min = cvScalar (0, smin, vmin, 0)
hsv_max = cvScalar (180, 256, vmax, 0)

#############################################################################
# some useful functions

def hsv2rgb (hue):
    # convert the hue value to the corresponding rgb value

    sector_data = [[0, 2, 1],
                   [1, 2, 0],
                   [1, 0, 2],
                   [2, 0, 1],
                   [2, 1, 0],
                   [0, 1, 2]]
    hue *= 0.1 / 3
    sector = cvFloor (hue)
    p = cvRound (255 * (hue - sector))
    if sector & 1:
        p ^= 255

    rgb = {}
    rgb [sector_data [sector][0]] = 255
    rgb [sector_data [sector][1]] = 0
    rgb [sector_data [sector][2]] = p

    return cvScalar (rgb [2], rgb [1], rgb [0], 0)

#############################################################################
# so, here is the main part of the program

if __name__ == '__main__':

    # a small welcome
    print "OpenCV Python wrapper test"
    print "OpenCV version: %s (%d, %d, %d)" % (CV_VERSION,
                                               CV_MAJOR_VERSION,
                                               CV_MINOR_VERSION,
                                               CV_SUBMINOR_VERSION)

    # first, create the necessary windows
    cvNamedWindow ('Camera', CV_WINDOW_AUTOSIZE)
    cvNamedWindow ('Histogram', CV_WINDOW_AUTOSIZE)

    # move the new window to a better place
    cvMoveWindow ('Camera', 10, 40)
    cvMoveWindow ('Histogram', 10, 270)

    try:
        # try to get the device number from the command line
        device = int (sys.argv [1])

        # got it ! so remove it from the arguments
        del sys.argv [1]
    except (IndexError, ValueError):
        # no device number on the command line, assume we want the 1st device
        device = 0

    if len (sys.argv) == 1:
        # no argument on the command line, try to use the camera
        capture = cvCreateCameraCapture (device)

        # set the wanted image size from the camera
        cvSetCaptureProperty (capture,
                                      CV_CAP_PROP_FRAME_WIDTH, 320)
        cvSetCaptureProperty (capture,
                                      CV_CAP_PROP_FRAME_HEIGHT,240)
    else:
        # we have an argument on the command line,
        # we can assume this is a file name, so open it
        capture = cvCreateFileCapture (sys.argv [1])            

    # check that capture device is OK
    if not capture:
        print "Error opening capture device"
        sys.exit (1)
        
    # create an image to put in the histogram
    histimg = cvCreateImage (cvSize (320,240), 8, 3)
    
    # init the image of the histogram to black
    cvSetZero (histimg)
    
    # capture the 1st frame to get some propertie on it
    frame = cvQueryFrame (capture)

    # get some properties of the frame
    frame_size = cvGetSize (frame)

    # compute which selection of the frame we want to monitor
    selection = cvRect (0, 0, frame.width, frame.height)

    # create some images usefull later
    hue = cvCreateImage (frame_size, 8, 1)
    mask = cvCreateImage (frame_size, 8, 1)
    hsv = cvCreateImage (frame_size, 8, 3 )
    
    # create the histogram
    hist = cvCreateHist ([hdims], CV_HIST_ARRAY, hranges, 1)

    while 1:
        # do forever

        # 1. capture the current image
        frame = cvQueryFrame (capture)
        if frame is None:
            # no image captured... end the processing
            break

        # mirror the captured image
        cvFlip (frame, None, 1)

        # compute the hsv version of the image 
        cvCvtColor (frame, hsv, CV_BGR2HSV)

        # compute which pixels are in the wanted range
        cvInRangeS (hsv, hsv_min, hsv_max, mask)

        # extract the hue from the hsv array
        cvSplit (hsv, hue, None, None, None)
        
        # select the rectangle of interest in the hue/mask arrays
        hue_roi = cvGetSubRect (hue, None, selection)
        mask_roi = cvGetSubRect (mask, None, selection)
        
        # it's time to compute the histogram
        cvCalcHist ([hue_roi], hist, 0, mask_roi)

        # extract the min and max value of the histogram
        min_val, max_val = cvGetMinMaxHistValue(hist)
        
        # compute the scale factor
        if max_val > 0:
            scale = 255. / max_val
        else:
            scale = 0.
            
        hbins = hist.bins[0]

        # scale the histograms
        cvConvertScale (hbins, hbins, scale, 0)

        # clear the histogram image
        cvSetZero (histimg)

        # compute the width for each bin do display
        bin_w = histimg.width / hdims
        
        for  i in range (hdims):
            # for all the bins

            # get the value, and scale to the size of the hist image
            val = cvRound (cvGetReal1D (hbins, i)
                              * histimg.height / 255)

            # compute the color
            color = hsv2rgb (i * 180. / hdims)

            # draw the rectangle in the wanted color
            cvRectangle (histimg,
                            cvPoint (i * bin_w, histimg.height),
                            cvPoint ((i + 1) * bin_w, histimg.height - val),
                            color, -1, 8, 0)

        # we can now display the images
        cvShowImage ('Camera', frame)
        cvShowImage ('Histogram', histimg)

        # handle events
        if cvWaitKey (10) & 255 == 27:
            # user has press the ESC key, so exit
            break
