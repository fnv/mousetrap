#!/usr/bin/env python

# OpenCV's Python demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv
"""
This program is demonstration for ellipse fitting. Program finds 
contours and approximate it by ellipses.

Trackbar specify threshold parametr.

White lines is contours. Red lines is fitting ellipses.

Original C implementation by:  Denis Burenkov.
Python implementation by: Roman Stanchak
"""

import sys
from opencv import *

image02 = None
image03 = None
image04 = None

def process_image( slider_pos ): 
    """
    Define trackbar callback functon. This function find contours,
    draw it and approximate it by ellipses.
    """
    stor = cvCreateMemStorage(0);
    
    # Threshold the source image. This needful for cvFindContours().
    cvThreshold( image03, image02, slider_pos, 255, CV_THRESH_BINARY );
    
    # Find all contours.
    nb_contours, cont = cvFindContours (image02, stor, method=CV_CHAIN_APPROX_NONE)
    
    # Clear images. IPL use.
    cvZero(image02);
    cvZero(image04);
    
    if cont is not None:
        # This cycle draw all contours and approximate it by ellipses.
        for c in cont.hrange():
            count = c.total; # This is number point in contour

            # Number point must be more than or equal to 6 (for cvFitEllipse_32f).        
            if( count < 6 ):
                continue;
            
            # Alloc memory for contour point set.    
            PointArray = cvCreateMat(1, count, CV_32SC2)
            PointArray2D32f= cvCreateMat( 1, count, CV_32FC2)
            
            # Get contour point set.
            cvCvtSeqToArray(c, PointArray.data.ptr, cvSlice(0, CV_WHOLE_SEQ_END_INDEX));
            
            # Convert CvPoint set to CvBox2D32f set.
            cvConvert( PointArray, PointArray2D32f )
            
            box = CvBox2D()

            # Fits ellipse to current contour.
            box = cvFitEllipse2(PointArray2D32f);
            
            # Draw current contour.
            cvDrawContours(image04, c, CV_RGB(255,255,255), CV_RGB(255,255,255),0,1,8,cvPoint(0,0));
            
            # Convert ellipse data from float to integer representation.
            center = CvPoint()
            size = CvSize()
            center.x = cvRound(box.center.x);
            center.y = cvRound(box.center.y);
            size.width = cvRound(box.size.width*0.5);
            size.height = cvRound(box.size.height*0.5);
            box.angle = -box.angle;
            
            # Draw ellipse.
            cvEllipse(image04, center, size,
                      box.angle, 0, 360,
                      CV_RGB(0,0,255), 1, CV_AA, 0);
    
    # Show image. HighGUI use.
    cvShowImage( "Result", image04 );


if __name__ == '__main__':
    argc = len(sys.argv)
    filename = "stuff.jpg"
    if(argc == 2):
        filename = sys.argv[1]
    
    slider_pos = 70

    # load image and force it to be grayscale
    image03 = cvLoadImage(filename, 0)
    if not image03:
        print "Could not load image " + filename
        sys.exit(-1)

    # Create the destination images
    image02 = cvCloneImage( image03 );
    image04 = cvCloneImage( image03 );

    # Create windows.
    cvNamedWindow("Source", 1);
    cvNamedWindow("Result", 1);

    # Show the image.
    cvShowImage("Source", image03);

    # Create toolbars. HighGUI use.
    cvCreateTrackbar( "Threshold", "Result", slider_pos, 255, process_image );


    process_image( slider_pos );

    #Wait for a key stroke; the same function arranges events processing                
    print "Press any key to exit"
    cvWaitKey(0);

    cvDestroyWindow("Source");
    cvDestroyWindow("Result");

