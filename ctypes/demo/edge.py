#!/usr/bin/env python
# OpenCV's Python demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv

print "OpenCV Python version of edge"

import sys

# import the necessary things for OpenCV
from opencv import *

# some definitions
win_name = "Edge"
trackbar_name = "Threshold"

# the callback on the trackbar
def on_trackbar (position):

    cvSmooth (gray, edge, CV_BLUR, 3, 3, 0)
    cvNot (gray, edge)

    # run the edge dector on gray scale
    cvCanny (gray, edge, position, position * 3, 3)

    # reset
    cvSetZero (col_edge)

    # copy edge points
    cvCopy (image, col_edge, edge)
    
    # show the image
    cvShowImage (win_name, col_edge)

if __name__ == '__main__':
    filename = "fruits.jpg"

    if len(sys.argv)>1:
        filename = sys.argv[1]

    # load the image gived on the command line
    image = cvLoadImage (filename)

    if not image:
        print "Error loading image '%s'" % filename
        sys.exit(-1)

    # create the output image
    col_edge = cvCreateImage (cvSize (image.width, image.height), 8, 3)

    # convert to grayscale
    gray = cvCreateImage (cvSize (image.width, image.height), 8, 1)
    edge = cvCreateImage (cvSize (image.width, image.height), 8, 1)
    cvCvtColor (image, gray, CV_BGR2GRAY)

    # create the window
    cvNamedWindow (win_name, CV_WINDOW_AUTOSIZE)

    # create the trackbar
    cvCreateTrackbar (trackbar_name, win_name, 1, 100, on_trackbar)

    # show the image
    on_trackbar (0)

    # wait a key pressed to end
    cvWaitKey (0)
