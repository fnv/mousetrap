#!/usr/bin/env python
# OpenCV 1.1's C demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv

#
# A Demo to OpenCV Implementation of SURF
# Further Information Refer to "SURF: Speed-Up Robust Feature"
# Author: Liu Liu
# liuliu.1987+opencv@gmail.com
#

from sys import argv, stderr
from ctypes import *
from opencv import *

image = None

def compareSURFDescriptors(d1, d2, best, length):
    total_cost = 0
    assert( length % 4 == 0 )
    for i in xrange(0, length, 4):
        t0 = d1[i] - d2[i]
        t1 = d1[i+1] - d2[i+1]
        t2 = d1[i+2] - d2[i+2]
        t3 = d1[i+3] - d2[i+3]
        total_cost += t0*t0 + t1*t1 + t2*t2 + t3*t3
        if total_cost > best:
            break
    return total_cost

def naiveNearestNeighbor(vec, laplacian, model_keypoints, model_descriptors):
    length = model_descriptors.elem_size/sizeof(c_float)
    neighbor = -1
    dist1 = 1e6
    dist2 = 1e6
    kp_arr = model_keypoints.asarray(CvSURFPoint)
    mv_arr = model_descriptors.asarrayptr(POINTER(c_float))

    for i in xrange(model_descriptors.total):
        if  laplacian != kp_arr[i].laplacian:
            continue
        d = compareSURFDescriptors(vec, mv_arr[i], dist2, length)
        if d < dist1:
            dist2 = dist1
            dist1 = d
            neighbor = i
        elif d < dist2:
            dist2 = d

    if dist1 < 0.6*dist2:
        return neighbor
    return -1

def findPairs(objectKeypoints, objectDescriptors, imageKeypoints, imageDescriptors):
    ptpairs = []
    kp_arr = objectKeypoints.asarray(CvSURFPoint)
    de_arr = objectDescriptors.asarrayptr(POINTER(c_float))

    for i in xrange(objectDescriptors.total):
        nn = naiveNearestNeighbor( de_arr[i], kp_arr[i].laplacian, imageKeypoints, imageDescriptors );
        if nn >= 0:
            ptpairs.append((i,nn))
    
    return ptpairs

# a rough implementation for object location
def locatePlanarObject(objectKeypoints, objectDescriptors, imageKeypoints, imageDescriptors, src_corners, dst_corners):
    ptpairs = findPairs(objectKeypoints, objectDescriptors, imageKeypoints, imageDescriptors)
    n = len(ptpairs)
    if n < 4:
        return 0

    ok_arr = objectKeypoints.asarray(CvSURFPoint)
    pt1 = cvCreateMatFromCvPoint2D32fList([ok_arr[x[0]].pt for x in ptpairs])
    ik_arr = imageKeypoints.asarray(CvSURFPoint)
    pt2 = cvCreateMatFromCvPoint2D32fList([ik_arr[x[1]].pt for x in ptpairs])
    try:
        h = cvFindHomography( pt1, pt2, method=CV_RANSAC, ransacReprojThreshold=5 )[0]
    except RuntimeError:
        return 0

    for i in xrange(4):
        x = src_corners[i].x
        y = src_corners[i].y
        Z = 1./(h[2,0]*x + h[2,1]*y + h[2,2])
        X = (h[0,0]*x + h[0,1]*y + h[0,2])*Z
        Y = (h[1,0]*x + h[1,1]*y + h[1,2])*Z
        dst_corners[i] = cvPoint(cvRound(X), cvRound(Y))

    return 1

if __name__ == '__main__':
    if len(argv) == 3:
        object_filename = argv[1]
        scene_filename = argv[2]
    else:
        object_filename = "box.png"
        scene_filename = "box_in_scene.png"
        
    if cvVersion < 110:
        print >> stderr, "You need OpenCV 1.1 installed for this demo to work. OpenCV version", CV_VERSION, " is detected."
        exit(-1)
        
    print "Warning: function findPairs() implemented in this demo is *very* slow, due to too many low-level computations. Be patient, or rewrite a faster implementation for this function (e.g. in C/C++ or SciPy).\n"

    storage = cvCreateMemStorage(0)

    cvNamedWindow("Object", 1)
    cvNamedWindow("Object Correspond", 1)

    colors = (CvScalar*9)(
        (0,0,255),
        (0,128,255),
        (0,255,255),
        (0,255,0),
        (255,128,0),
        (255,255,0),
        (255,0,0),
        (255,0,255),
        (255,255,255),
    )

    object = cvLoadImage( object_filename, CV_LOAD_IMAGE_GRAYSCALE )
    image = cvLoadImage( scene_filename, CV_LOAD_IMAGE_GRAYSCALE )
    if not object or not image:
        print >> stderr, "Can not load %s and/or %s\n" \
            "Usage: find_obj [<object_filename> <scene_filename>]\n" \
            % (object_filename, scene_filename)
        exit(-1)
    
    object_color = cvCreateImage(cvGetSize(object), 8, 3)
    cvCvtColor( object, object_color, CV_GRAY2BGR )
    
    imageKeypoints = None
    imageDescriptors = None
    params = cvSURFParams(500, 1)

    tt = float(cvGetTickCount())
    objectKeypoints, objectDescriptors = cvExtractSURF( object, None, None, True, storage, params )
    print "Object Descriptors: %d\n" % objectDescriptors.total
    imageKeypoints, imageDescriptors = cvExtractSURF( image, None, None, True, storage, params )
    print "Image Descriptors: %d\n" % imageDescriptors.total
    tt = float(cvGetTickCount()) - tt
    print "Extraction time = %gms\n" % (tt/(cvGetTickFrequency()*1000.))
    src_corners = (CvPoint*4)((0,0), (object.width,0), (object.width, object.height), (0, object.height))
    dst_corners = (CvPoint*4)()
    correspond = cvCreateImage( cvSize(image.width, object.height+image.height), 8, 1 )
    cvSetImageROI( correspond, cvRect( 0, 0, object.width, object.height ) )
    cvCopy( object, correspond )
    cvSetImageROI( correspond, cvRect( 0, object.height, correspond.width, correspond.height ) )
    cvCopy( image, correspond )
    cvResetImageROI( correspond )
    if locatePlanarObject( objectKeypoints, objectDescriptors, imageKeypoints, imageDescriptors, src_corners, dst_corners ):
        for i in xrange(4):
            r1 = dst_corners[i%4]
            r2 = dst_corners[(i+1)%4]
            cvLine( correspond, cvPoint(r1.x, r1.y+object.height ), cvPoint(r2.x, r2.y+object.height ), colors[8] )

    ptpairs = findPairs(objectKeypoints, objectDescriptors, imageKeypoints, imageDescriptors)
    for i in xrange(len(ptpairs)):
        r1 = CV_GET_SEQ_ELEM(CvSURFPoint, objectKeypoints, ptpairs[i][0])[0]
        r2 = CV_GET_SEQ_ELEM(CvSURFPoint, imageKeypoints, ptpairs[i][1])[0]
        cvLine( correspond, cvPointFrom32f(r1.pt), cvPoint(cvRound(r2.pt.x), cvRound(r2.pt.y+object.height)), colors[8] )

    cvShowImage( "Object Correspond", correspond )
    for i in xrange(objectKeypoints.total):
        r = CV_GET_SEQ_ELEM(CvSURFPoint, objectKeypoints, i )[0]
        cvCircle( object_color, cvPoint(cvRound(r.pt.x), cvRound(r.pt.y)), cvRound(r.size*1.2/9.*2), colors[0], 1, 8, 0 )

    cvShowImage( "Object", object_color )

    cvWaitKey(0)
