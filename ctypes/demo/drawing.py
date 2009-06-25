#!/usr/bin/env python
# OpenCV's Python demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv

print "OpenCV Python version of drawing"

# import the necessary things for OpenCV
from opencv import *

# for making random numbers
from random import Random

def random_color (random):
    """
    Return a random color
    """
    icolor = random.randint (0, 0xFFFFFF)
    return cvScalar (icolor & 0xff, (icolor >> 8) & 0xff, (icolor >> 16) & 0xff)

if __name__ == '__main__':

    # some "constants"
    width = 1000
    height = 700
    window_name = "Drawing Demo"
    number = 100
    delay = 5
    line_type = CV_AA  # change it to 8 to see non-antialiased graphics
    
    # create the source image
    image = cvCreateImage (cvSize (width, height), 8, 3)

    # create window and display the original picture in it
    cvNamedWindow (window_name, 1)
    cvSetZero (image)
    cvShowImage (window_name, image)

    # create the random number
    random = Random ()

    # draw some lines
    for i in range (number):
        pt1 = cvPoint (random.randrange (-width, 2 * width),
                          random.randrange (-height, 2 * height))
        pt2 = cvPoint (random.randrange (-width, 2 * width),
                          random.randrange (-height, 2 * height))
        cvLine (image, pt1, pt2,
                   random_color (random),
                   random.randrange (0, 10),
                   line_type, 0)
        
        cvShowImage (window_name, image)
        cvWaitKey (delay)

    # draw some rectangles
    for i in range (number):
        pt1 = cvPoint (random.randrange (-width, 2 * width),
                          random.randrange (-height, 2 * height))
        pt2 = cvPoint (random.randrange (-width, 2 * width),
                          random.randrange (-height, 2 * height))
        cvRectangle (image, pt1, pt2,
                        random_color (random),
                        random.randrange (-1, 9),
                        line_type, 0)
        
        cvShowImage (window_name, image)
        cvWaitKey (delay)

    # draw some ellipes
    for i in range (number):
        pt1 = cvPoint (random.randrange (-width, 2 * width),
                          random.randrange (-height, 2 * height))
        sz = cvSize (random.randrange (0, 200),
                        random.randrange (0, 200))
        angle = random.randrange (0, 1000) * 0.180
        cvEllipse (image, pt1, sz, angle, angle - 100, angle + 200,
                        random_color (random),
                        random.randrange (-1, 9),
                        line_type, 0)
        
        cvShowImage (window_name, image)
        cvWaitKey (delay)

    # init the list of polylines
    nb_polylines = 2
    polylines_size = 3
    pt = [0,] * nb_polylines
    for a in range (nb_polylines):
        pt [a] = [0,] * polylines_size

    # draw some polylines
    for i in range (number):
        for a in range (nb_polylines):
            for b in range (polylines_size):
                pt [a][b] = cvPoint (random.randrange (-width, 2 * width),
                                     random.randrange (-height, 2 * height))
        cvPolyLine (image, pt, 1,
                       random_color (random),
                       random.randrange (1, 9),
                       line_type, 0)

        cvShowImage (window_name, image)
        cvWaitKey (delay)

    # draw some filled polylines
    for i in range (number):
        for a in range (nb_polylines):
            for b in range (polylines_size):
                pt [a][b] = cvPoint (random.randrange (-width, 2 * width),
                                     random.randrange (-height, 2 * height))
        cvFillPoly (image, pt,
                       random_color (random),
                       line_type, 0)

        cvShowImage (window_name, image)
        cvWaitKey (delay)

    # draw some circles
    for i in range (number):
        pt1 = cvPoint (random.randrange (-width, 2 * width),
                          random.randrange (-height, 2 * height))
        cvCircle (image, pt1, random.randrange (0, 300),
                     random_color (random),
                     random.randrange (-1, 9),
                     line_type, 0)
        
        cvShowImage (window_name, image)
        cvWaitKey (delay)

    # draw some text
    for i in range (number):
        pt1 = cvPoint (random.randrange (-width, 2 * width),
                          random.randrange (-height, 2 * height))
        font = cvInitFont (None, random.randrange (0, 8),
                              random.randrange (0, 100) * 0.05 + 0.01,
                              random.randrange (0, 100) * 0.05 + 0.01,
                              random.randrange (0, 5) * 0.1,
                              random.randrange (0, 10),
                              line_type)

        cvPutText (image, "Testing text rendering!",
                      pt1, font,
                      random_color (random))
        
        cvShowImage (window_name, image)
        cvWaitKey (delay)

    # prepare a text, and get it's properties
    font = cvInitFont (None, CV_FONT_HERSHEY_COMPLEX,
                          3, 3, 0.0, 5, line_type)
    text_size, ymin = cvGetTextSize ("OpenCV forever!", font)
    pt1.x = (width - text_size.width) / 2
    pt1.y = (height + text_size.height) / 2
    image2 = cvCloneImage(image)

    # now, draw some OpenCV pub ;-)
    for i in range (255):
        cvSubS (image2, cvScalarAll (i), image, None)
        cvPutText (image, "OpenCV forever!",
                      pt1, font, cvScalar (255, i, i))
        cvShowImage (window_name, image)
        cvWaitKey (delay)

    # wait some key to end
    cvWaitKey (0)
