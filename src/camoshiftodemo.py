#!/usr/bin/env python
# OpenCV's C demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv

from ctypes import c_int
from ctypesopencv import *
from sys import argv, exit
import math

image = None
hsv = None
hue = None
mask = None
backproject = None
histimg = None
hist = None

backproject_mode = 0
select_object = 0
track_object = 0
show_hist = 1
origin = None
selection = None
track_window = None
track_box = None
track_comp = None
hdims = 16

# initial settings for value, saturation, and hue
vmin = c_int(10)
vmax = c_int(256)
smin = c_int(80)
smax = c_int(256)
hmin = c_int(25)
hmax = c_int(40) #this may have to be 180 and not 256, for whatever reason
h2min = c_int(170)
h2max = c_int(175)

#runs when a mouse event (motion or clicking) occurs
def on_mouse(event, x, y, flags, param):
    global select_object, image, selection, origin, track_object
    
    if image is None:
        return

    if image.origin:
        y = image.height - y

    if select_object:
        selection.x = min(x,origin.x)
        selection.y = min(y,origin.y)
        selection.width = selection.x + abs(x - origin.x)
        selection.height = selection.y + abs(y - origin.y)
        
        selection.x = max( selection.x, 0 )
        selection.y = max( selection.y, 0 )
        selection.width = min( selection.width, image.width )
        selection.height = min( selection.height, image.height )
        selection.width -= selection.x
        selection.height -= selection.y

    if event == CV_EVENT_LBUTTONDOWN:
        origin = cvPoint(x,y)
        selection = cvRect(x,y,0,0)
        select_object = 1
    elif event == CV_EVENT_LBUTTONUP:
        select_object = 0
        if selection.width > 0 and selection.height > 0:
            track_object = -1


def hsv2rgb(hue):
    rgb=[0,0,0]
    
    sector_data= ((0,2,1), (1,2,0), (1,0,2), (2,0,1), (2,1,0), (0,1,2))
    hue *= 0.033333333333333333333333333333333
    sector = cvFloor(hue)
    p = cvRound(255*(hue - sector))
    p ^= 255 if bool(sector & 1) else 0

    rgb[sector_data[sector][0]] = 255
    rgb[sector_data[sector][1]] = 0
    rgb[sector_data[sector][2]] = p

    return cvScalar(rgb[2], rgb[1], rgb[0], 0)

#main method
if __name__ == '__main__':
    argc = len(argv)    
    if argc == 1 or (argc == 2 and argv[1].isdigit()):
        capture = cvCaptureFromCAM( int(argv[1]) if argc == 2 else 0 )
    elif argc == 2:
        capture = cvCaptureFromAVI( argv[1] )
    else:
        capture = None

    if not capture:
        print "Could not initialize capturing..."
        exit(-1)

    print "Hot keys: \n" \
        "\tESC - quit the program\n" \
        "\tc - stop the tracking\n" \
        "\tb - switch to/from backprojection view\n" \
        "\th - show/hide object histogram\n" \
        "To initialize tracking, select the object with mouse\n"
    print "ASIHDDSF"

    cvNamedWindow( "Histogram", 1 )
    cvNamedWindow( "CamShiftDemo", 1 )
    cvNamedWindow( "Mask", 1 )
    #cvNamedWindow( "Backproject", 1)
    #cvNamedWindow( "Hue", 1)

    cvSetMouseCallback( "CamShiftDemo", on_mouse )

    #cvCreateTrackbar( "Vmin", "CamShiftDemo", vmin, 256 )
    #cvCreateTrackbar( "Vmax", "CamShiftDemo", vmax, 256 )
    #cvCreateTrackbar( "Smin", "CamShiftDemo", smin, 256 )
    #cvCreateTrackbar( "Smax", "CamShiftDemo", smax, 256 )
    cvCreateTrackbar( "Hmin", "CamShiftDemo", hmin, 180 )
    cvCreateTrackbar( "Hmax", "CamShiftDemo", hmax, 180 )
    cvCreateTrackbar( "H2min", "CamShiftDemo", h2min, 180 )
    cvCreateTrackbar( "H2max", "CamShiftDemo", h2max, 180 )

    while True:
        frame = cvQueryFrame( capture )
        if not frame:
            break

        if not image:
            # allocate all the buffers
            image = cvCreateImage( cvGetSize(frame), 8, 3 )
            image.origin = frame.origin
            hsv = cvCreateImage( cvGetSize(frame), 8, 3 )
            hue = cvCreateImage( cvGetSize(frame), 8, 1 )
            mask = cvCreateImage( cvGetSize(frame), 8, 1 )
            mask2 = cvCreateImage( cvGetSize(frame), 8, 1 )
            maskcombo = cvCreateImage( cvGetSize(frame), 8, 1 )
            backproject = cvCreateImage( cvGetSize(frame), 8, 1 )
            hist = cvCreateHist( [hdims], CV_HIST_ARRAY, [[0, 180]] )
            histimg = cvCreateImage( cvSize(320,200), 8, 3 )
            cvZero( histimg )

        cvCopy(frame, image)
        cvCvtColor( image, hsv, CV_BGR2HSV )

        if track_object != 0:
            #updates the hsv values
            cvInRangeS( hsv, cvScalar(hmin.value,smin.value,min(vmin.value,vmax.value),0),
                        cvScalar(hmax.value,smax.value,max(vmin.value,vmax.value),0), mask )
            cvInRangeS( hsv, cvScalar(h2min.value,smin.value,min(vmin.value,vmax.value),0),
                        cvScalar(h2max.value,smax.value,max(vmin.value,vmax.value),0), mask2 )
            cvSplit(hsv, hue)

            cvOr(mask, mask2, maskcombo)

            if track_object < 0:
                cvSetImageROI( hue, selection )
                cvSetImageROI( maskcombo, selection )
                cvCalcHist( [hue], hist, 0, maskcombo );
                min_val, max_val = cvGetMinMaxHistValue(hist)
                hbins = hist.bins[0]
                cvConvertScale( hbins, hbins, 255. / max_val if max_val else 0., 0 )
                cvResetImageROI( hue )
                cvResetImageROI( maskcombo )
                track_window = selection
                track_object = 1

                cvZero( histimg )
                bin_w = histimg.width / hdims
                for i in xrange(hdims):
                    val = cvRound( cvGetReal1D(hbins,i)*histimg.height/255 )
                    color = hsv2rgb(i*180./hdims)
                    cvRectangle( histimg, cvPoint(i*bin_w,histimg.height),
                                 cvPoint((i+1)*bin_w,histimg.height - val),
                                 color, -1, 8, 0 )

            cvCalcBackProject( [hue], backproject, hist )
            cvAnd(backproject, maskcombo, backproject)
            #CAMSHIFT HAPPENS
            niter, track_comp, track_box = cvCamShift( backproject, track_window,
                        cvTermCriteria( CV_TERMCRIT_EPS | CV_TERMCRIT_ITER, 10, 1 ))
            track_window = track_comp.rect
            
            if backproject_mode:
                cvCvtColor( backproject, image, CV_GRAY2BGR )
            if not image.origin:
                track_box.angle = -track_box.angle
            # Make sure its a number.
            if math.isnan(track_box.size.height): 
                track_box.size.height = 0
            if math.isnan(track_box.size.width): 
                track_box.size.width = 0
            cvEllipseBox( image, track_box, CV_RGB(255,0,0), 3, CV_AA, 0 )
        
        if bool(select_object) and selection.width > 0 and selection.height > 0:
            cvSetImageROI( image, selection )
            cvXorS( image, cvScalarAll(255), image )
            cvResetImageROI( image )

        cvShowImage( "CamShiftDemo", image )
        cvShowImage( "Histogram", histimg )
        cvShowImage( "Mask", maskcombo )
        #cvShowImage( "Backproject", backproject)
        #cvShowImage( "Hue", hue)

        c = '%c' % (cvWaitKey(10) & 255)
        if c == '\x1b':
            break
        elif c == 'b':
            backproject_mode ^= 1
        elif c =='c':
            track_object = 0
            cvZero( histimg )
        elif c =='h':
            show_hist ^= 1
            if not show_hist:
                cvDestroyWindow( "Histogram" )
            else:
                cvNamedWindow( "Histogram", 1 )

