#! /usr/bin/env python

import sys

# import the necessary things for OpenCV
from opencv import cv
from opencv import highgui

#############################################################################
# definition of some constants

# how many bins we want for the histogram, and their ranges
hdims = 32
hranges = [[0, 180]]

# ranges for the limitation of the histogram
vmin = 10
vmax = 256
smin = 30
smax = 256
hmin = 0
hmax = 180

#has a selection been made?

select_object = 0
last_event = -1

origin = None

# the range we want to monitor
hsv_min = cv.cvScalar (hmin, smin, vmin, 0)
hsv_max = cv.cvScalar (hmax, smax, vmax, 0)

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
    sector = cv.cvFloor (hue)
    p = cv.cvRound (255 * (hue - sector))
    if sector & 1:
        p ^= 255

    rgb = {}
    rgb [sector_data [sector][0]] = 255
    rgb [sector_data [sector][1]] = 0
    rgb [sector_data [sector][2]] = p

    return cv.cvScalar (rgb [2], rgb [1], rgb [0], 0)

#callback functions to update trackbar values

def change_vmax(p):
    global vmax
    vmax = p

def change_vmin(p):
    global vmin
    vmin = p

def change_smin(p):
    global smin
    smin = p

def change_hmax(p):
    global hmax
    hmax = p

def change_hmin(p):
    global hmin
    hmin = p

def change_smax(p):
    global smax
    smax = p

# Mouse selecting isn't working and I don't know why!!!!!
def on_mouse( event, x, y, flags, param ):

    global origin
    global selection

    if (event != last_event):
        print(str(event))
        global last_event
        last_event = event

    if (not frame):
        return

    """if( frame.origin ):
        y = frame.height - y"""

    global select_object
    if( select_object ):
    
        selection.x = min(x,origin.x)
        selection.y = min(y,origin.y)
        selection.width = selection.x + abs(x - origin.x)
        selection.height = selection.y + abs(y - origin.y)
        
        selection.x = max( selection.x, 0 )
        selection.y = max( selection.y, 0 )
        selection.width = min( selection.width, frame.width )
        selection.height = min( selection.height, frame.height )
        selection.width -= selection.x
        selection.height -= selection.y
    
    if (event == 1):
        origin = cv.cvPoint(x,y)
        selection = cv.cvRect(x,y,1,1)
        select_object = 1
        
    if (event == 4):
        select_object = 0
        if( selection.width > 0 and selection.height > 0 ):
            print("selected")
            #track_object = -1
                # select the rectangle of interest in the hue/mask arrays

        hue_roi = cv.cvGetSubRect (hue, selection)
        mask_roi = cv.cvGetSubRect (mask, selection)

        # it's time to compute the histogram
        cv.cvCalcHist (hue_roi, hist, 0, mask_roi)

        # extract the min and max value of the histogram
        min_val, max_val = cv.cvGetMinMaxHistValue (hist, None, None)

        # compute the scale factor
        if max_val > 0:
            scale = 255. / max_val
        else:
            scale = 0.

        # scale the histograms
        cv.cvConvertScale (hist.bins, hist.bins, scale, 0)

        # clear the histogram image
        cv.cvSetZero (histimg)

        # compute the width for each bin do display
        bin_w = histimg.width / hdims
        
        for  i in range (hdims):
            # for all the bins

            # get the value, and scale to the size of the hist image
            val = cv.cvRound (cv.cvGetReal1D (hist.bins, i)
                              * histimg.height / 255)

            # compute the color
            color = hsv2rgb (i * 180. / hdims)

            # draw the rectangle in the wanted color
            cv.cvRectangle (histimg,
                            cv.cvPoint (i * bin_w, histimg.height),
                            cv.cvPoint ((i + 1) * bin_w, histimg.height - val),
                            color, -1, 8, 0)


#############################################################################
# so, here is the main part of the program

if __name__ == '__main__':

    # a small welcome
    print "OpenCV Python wrapper test"
    print "OpenCV version: %s (%d, %d, %d)" % (cv.CV_VERSION,
                                               cv.CV_MAJOR_VERSION,
                                               cv.CV_MINOR_VERSION,
                                               cv.CV_SUBMINOR_VERSION)

    # first, create the necessary windows
    highgui.cvNamedWindow ('Camera', highgui.CV_WINDOW_AUTOSIZE)
    highgui.cvNamedWindow ('Histogram', highgui.CV_WINDOW_AUTOSIZE)
    highgui.cvNamedWindow ('HSV View', highgui.CV_WINDOW_AUTOSIZE)
    highgui.cvNamedWindow ('Mask', highgui.CV_WINDOW_AUTOSIZE)

    #These trackbars allow you to change HSV values (they didn't fit in one window)
    highgui.cvCreateTrackbar( "Hmin", "Mask", hmin, 180, change_hmin );
    highgui.cvCreateTrackbar( "Hmax", "Mask", hmax, 180, change_hmax );
    highgui.cvCreateTrackbar( "Smin", "Camera", smin, 256, change_smin );
    highgui.cvCreateTrackbar( "Smax", "Camera", smax, 256, change_smax );
    highgui.cvCreateTrackbar( "Vmin", "Camera", vmin, 256, change_vmin );
    highgui.cvCreateTrackbar( "Vmax", "Camera", vmax, 256, change_vmax );

    highgui.cvSetMouseCallback( "Camera", on_mouse)

    # move the new window to a better place
    highgui.cvMoveWindow ('Camera', 10, 40)
    highgui.cvMoveWindow ('Histogram',750, 270)
    highgui.cvMoveWindow ('HSV View', 500, 40)
    highgui.cvMoveWindow ('Mask', 700, 270)

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
        capture = highgui.cvCreateCameraCapture (device)

        # set the wanted image size from the camera
        highgui.cvSetCaptureProperty (capture,
                                      highgui.CV_CAP_PROP_FRAME_WIDTH, 320)
        highgui.cvSetCaptureProperty (capture,
                                      highgui.CV_CAP_PROP_FRAME_HEIGHT,240)
    else:
        # we have an argument on the command line,
        # we can assume this is a file name, so open it
        capture = highgui.cvCreateFileCapture (sys.argv [1])            

    # check that capture device is OK
    if not capture:
        print "Error opening capture device"
        sys.exit (1)
        
    # create an image to put in the histogram
    histimg = cv.cvCreateImage (cv.cvSize (320,240), 8, 3)

    # init the image of the histogram to black
    cv.cvSetZero (histimg)

    # capture the 1st frame to get some propertie on it
    frame = highgui.cvQueryFrame (capture)

    # get some properties of the frame
    frame_size = cv.cvGetSize (frame)

    # compute which selection of the frame we want to monitor
    selection = cv.cvRect (0, 0, frame.width, frame.height)

    # create some images usefull later
    hue = cv.cvCreateImage (frame_size, 8, 1)
    mask = cv.cvCreateImage (frame_size, 8, 1)
    hsv = cv.cvCreateImage (frame_size, 8, 3 )
    mask_yellow = cv.cvCreateImage (frame_size, 8, 1)
    mask_purple = cv.cvCreateImage (frame_size, 8, 1)

    # create the histogram
    hist = cv.cvCreateHist ([hdims], cv.CV_HIST_ARRAY, hranges, 1)

    while 1:
        # do forever

        # 1. capture the current image
        frame = highgui.cvQueryFrame (capture)
        if frame is None:
            # no image captured... end the processing
            break

        # mirror the captured image
        cv.cvFlip (frame, None, 1)

        # compute the hsv version of the image 
        cv.cvCvtColor (frame, hsv, cv.CV_BGR2HSV)

        # recalculate parameters since they might have been changed by the trackbar
        hsv_min = cv.cvScalar (hmin, smin, vmin, 0)
        hsv_max = cv.cvScalar (hmax, smax, vmax, 0)

        #hsv_min_yellow = cv.cvScalar (25, smin, vmin, 0)
        #hsv_max_yellow = cv.cvScalar (45, smax, vmax, 0)
        #hsv_min_purple = cv.cvScalar (165, smin, vmin, 0)
        #hsv_max_purple = cv.cvScalar (175, smax, vmax, 0)

        cv.cvInRangeS (hsv, hsv_min, hsv_max, mask)

        # compute which pixels are in the wanted range
        #cv.cvInRangeS (hsv, hsv_min_yellow, hsv_max_yellow, mask_yellow)
        #cv.cvInRangeS (hsv, hsv_min_purple, hsv_max_purple, mask_purple)

        # in c: pixel[row][col] = mask_yellow.imageData + row*mask_yellow.widthStep + col

        #print mask.imageData

        #cv.cvOr(mask_yellow, mask_purple, mask, None)

        # extract the hue from the hsv array
        cv.cvSplit (hsv, hue, None, None, None)

#HHAHAHAHAAH this is where all the histogram code was from

        # we can now display the images
        highgui.cvShowImage ('Camera', frame)
        highgui.cvShowImage ('HSV View', hsv)        
        highgui.cvShowImage ('Mask', mask)
        highgui.cvShowImage ('Histogram', histimg)

        # handle events
        k = highgui.cvWaitKey (10)

        if k == '\x1b':
            # user has press the ESC key, so exit
            break
