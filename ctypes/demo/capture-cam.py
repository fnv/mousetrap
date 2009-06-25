#!/usr/bin/env python
# OpenCV's Python demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv

import sys

# import the necessary things for OpenCV
from opencv import *

# the codec existing in cvcapp.cpp,
# need to have a better way to specify them in the future
# WARNING: I have see only MPEG1VIDEO working on my computer
H263 = 0x33363255
H263I = 0x33363249
MSMPEG4V3 = 0x33564944
MPEG4 = 0x58564944
MSMPEG4V2 = 0x3234504D
MJPEG = 0x47504A4D
MPEG1VIDEO = 0x314D4950
AC3 = 0x2000
MP2 = 0x50
FLV1 = 0x31564C46

#############################################################################
# so, here is the main part of the program

if __name__ == '__main__':

    # a small welcome
    print "OpenCV Python capture video"

    # first, create the necessary window
    cvNamedWindow ('Camera', CV_WINDOW_AUTOSIZE)

    # move the new window to a better place
    cvMoveWindow ('Camera', 10, 10)

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
    else:
        # we have an argument on the command line,
        # we can assume this is a file name, so open it
        capture = cvCreateFileCapture (sys.argv [1])            

    # check that capture device is OK
    if not capture:
        print "Error opening capture device"
        sys.exit (1)

    # capture the 1st frame to get some propertie on it
    frame = cvQueryFrame (capture)

    # get size of the frame
    frame_size = cvGetSize (frame)

    # get the frame rate of the capture device
    fps = cvGetCaptureProperty (capture, CV_CAP_PROP_FPS)
    if fps == 0:
        # no fps getted, so set it to 30 by default
        fps = 30

    # create the writer
    writer = cvCreateVideoWriter ("captured.avi", CV_FOURCC('X','v','i','D'),
                                          fps, frame_size, True)

    # check the writer is OK
    if not writer:
        print "Error opening writer"
        sys.exit (1)
        
    while 1:
        # do forever

        # 1. capture the current image
        frame = cvQueryFrame (capture)
        if frame is None:
            # no image captured... end the processing
            break

        # write the frame to the output file
        cvWriteFrame (writer, frame)

        # display the frames to have a visual output
        cvShowImage ('Camera', frame)

        # handle events
        if cvWaitKey (5) & 255 == 27:
            # user has press the ESC key, so exit
            break
