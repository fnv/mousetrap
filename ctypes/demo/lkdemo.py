#!/usr/bin/env python
# OpenCV's Python demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv

print "OpenCV Python version of lkdemo"

import sys

# import the necessary things for OpenCV
from opencv import *

#############################################################################
# some "constants"

win_size = 10
MAX_COUNT = 500

#############################################################################
# some "global" variables

image = None
pt = None
add_remove_pt = False
flags = 0
night_mode = False
need_to_init = False

#############################################################################
# the mouse callback

# the callback on the trackbar
def on_mouse (event, x, y, flags, param):

    # we will use the global pt and add_remove_pt
    global pt
    global add_remove_pt
    
    if image is None:
        # not initialized, so skip
        return

    if event == CV_EVENT_LBUTTONDOWN:
        # user has click, so memorize it
        pt = cvPoint (x, y)
        add_remove_pt = True

#############################################################################
# so, here is the main part of the program

if __name__ == '__main__':

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
        
    # display a small howto use it
    print "Hot keys: \n" \
          "\tESC - quit the program\n" \
          "\tr - auto-initialize tracking\n" \
          "\tc - delete all the points\n" \
          "\tn - switch the \"night\" mode on/off\n" \
          "To add/remove a feature point click it\n"

    # first, create the necessary windows
    cvNamedWindow ('LkDemo', CV_WINDOW_AUTOSIZE)

    # register the mouse callback
    cvSetMouseCallback ('LkDemo', on_mouse, None)

    while 1:
        # do forever

        # 1. capture the current image
        frame = cvQueryFrame (capture)
        if frame is None:
            # no image captured... end the processing
            break

        if image is None:
            # create the images we need
            image = cvCreateImage (cvGetSize (frame), 8, 3)
            image.origin = 0
            grey = cvCreateImage (cvGetSize (frame), 8, 1)
            prev_grey = cvCreateImage (cvGetSize (frame), 8, 1)
            pyramid = cvCreateImage (cvGetSize (frame), 8, 1)
            prev_pyramid = cvCreateImage (cvGetSize (frame), 8, 1)
            points = [[], []]

        # copy the frame, so we can draw on it
        if frame.origin:
            cvFlip(frame, image)
        else:
            cvCopy (frame, image)

        # create a grey version of the image
        cvCvtColor (image, grey, CV_BGR2GRAY)

        if night_mode:
            # night mode: only display the points
            cvSetZero (image)

        if need_to_init:
            # we want to search all the good points
            points[1] = cvGoodFeaturesToTrack(grey, None, None, None, MAX_COUNT, 0.01, 10)

            # refine the corner locations
            cvFindCornerSubPix (
                grey,
                points [1],
                cvSize (win_size, win_size), cvSize (-1, -1),
                cvTermCriteria (CV_TERMCRIT_ITER | CV_TERMCRIT_EPS,
                                   20, 0.03))
                                               
        elif len (points [0]) > 0:
            # we have points, so display them

            # calculate the optical flow
            points [1], status = cvCalcOpticalFlowPyrLK (
                prev_grey, grey, prev_pyramid, pyramid,
                points [0], None, None, 
                cvSize (win_size, win_size), 3,
                None, None,
                cvTermCriteria (CV_TERMCRIT_ITER|CV_TERMCRIT_EPS,
                                   20, 0.03),
                flags)

            # initializations
            point_counter = -1
            new_points = []
            
            for the_point in points [1]:
                # go trough all the points

                # increment the counter
                point_counter += 1
                
                if add_remove_pt:
                    # we have a point to add, so see if it is close to
                    # another one. If yes, don't use it
                    dx = pt.x - the_point.x
                    dy = pt.y - the_point.y
                    if dx * dx + dy * dy <= 25:
                        # too close
                        add_remove_pt = 0
                        continue

                if not status [point_counter]:
                    # we will disable this point
                    continue

                # this point is a correct point
                new_points.append (the_point)
                
                # draw the current point
                cvCircle (image, cvPointFrom32f(the_point),
                             3, cvScalar (0, 255, 0, 0),
                             -1, 8, 0)

            # set back the points we keep
            points [1] = new_points
            
        if add_remove_pt:
            # we want to add a point
            points [1].append (cvPointTo32f (pt))

            # refine the corner locations
            points [1][-1] = cvFindCornerSubPix (
                grey,
                [points [1][-1]],
                cvSize (win_size, win_size), cvSize (-1, -1),
                cvTermCriteria (CV_TERMCRIT_ITER | CV_TERMCRIT_EPS,
                                   20, 0.03))[0]

            # we are no more in "add_remove_pt" mode
            add_remove_pt = False

        # swapping
        prev_grey, grey = grey, prev_grey
        prev_pyramid, pyramid = pyramid, prev_pyramid
        points [0], points [1] = points [1], points [0]
        need_to_init = False
        
        # we can now display the image
        cvShowImage ('LkDemo', image)

        # handle events
        c = '%c' % (cvWaitKey (10) & 255)

        if c == '\x1b':
            # user has press the ESC key, so exit
            break

        # transform the code to one character
        # c = chr (c)

        # processing depending on the character
        if c in ['r', 'R']:
            need_to_init = True
        elif c in ['c', 'C']:
            points = [[], []]
        elif c in ['n', 'N']:
            night_mode = not night_mode
