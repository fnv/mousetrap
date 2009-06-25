#!/usr/bin/env python
# OpenCV's Python demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv

print "OpenCV Python version of convexhull"

# import the necessary things for OpenCV
from opencv import *

# to generate random values
import random

# how many points we want at max
_MAX_POINTS = 100

if __name__ == '__main__':

    # main object to get random values from
    my_random = random.Random ()

    # create the image where we want to display results
    image = cvCreateImage (cvSize (500, 500), 8, 3)

    # create the window to put the image in
    cvNamedWindow ('hull', CV_WINDOW_AUTOSIZE)

    while True:
        # do forever

        # get a random number of points
        count = my_random.randrange (0, _MAX_POINTS) + 1

        # initialisations
        points = []
        
        for i in range (count):
            # generate a random point
            points.append (cvPoint (
                my_random.randrange (0, image.width / 2) + image.width / 4,
                my_random.randrange (0, image.width / 2) + image.width / 4
                ))

        # compute the convex hull
        hull = cvConvexHull2 (cvCreateMatFromCvPointList(points))
        hull = hull.data.i[:hull.cols]

        # start with an empty image
        cvSetZero (image)

        for i in range (count):
            # draw all the points
            cvCircle (image, points [i], 2,
                         cvScalar (0, 0, 255, 0),
                         CV_FILLED, CV_AA, 0)

        # start the line from the last point
        pt0 = points [hull[-1]]
        
        for point_index in hull:
            # connect the previous point to the current one

            # get the current one
            pt1 = points [point_index]

            # draw
            cvLine (image, pt0, pt1,
                       cvScalar (0, 255, 0, 0),
                       1, CV_AA, 0)

            # now, current one will be the previous one for the next iteration
            pt0 = pt1

        # display the final image
        cvShowImage ('hull', image)

        # handle events, and wait a key pressed
        if cvWaitKey (0) & 255 == 27:
            # user has press the ESC key, so exit
            break
