#!/usr/bin/env python

# OpenCV's Python demo
# -- adapted by Minh-Tri Pham to work with ctypes-opencv
from opencv import *
MAX_CLUSTERS=5

if __name__ == "__main__":

    color_tab = [CV_RGB(255,0,0),CV_RGB(0,255,0),CV_RGB(100,100,255), CV_RGB(255,0,255),CV_RGB(255,255,0)]
    img = cvCreateImage(cvSize(500, 500), 8, 3)
    rng = cvRNG(-1)
    cvNamedWindow( "clusters", 1 )
        
    while True:
        cluster_count = cvRandInt(rng)%(MAX_CLUSTERS-1) + 2
        sample_count = cvRandInt(rng)%999 + 1
        points = cvCreateMat(sample_count, 1, CV_32FC2)
        clusters = cvCreateMat(sample_count, 1, CV_32SC1)
        
        # generate random sample from multigaussian distribution
        for k in range(cluster_count):
            first = k*sample_count/cluster_count
            last = (k+1)*sample_count/cluster_count if k != cluster_count else sample_count
            if first < last:
                cvRandArr(rng, cvGetRows(points, None, first, last), CV_RAND_NORMAL,
                    cvScalar(cvRandInt(rng)%img.width,cvRandInt(rng)%img.height), cvScalar(img.width*0.1,img.height*0.1))
        cvRandShuffle( points, rng )
        
        # K Means Clustering
        cvKMeans2(points, cluster_count, clusters, cvTermCriteria(CV_TERMCRIT_EPS+CV_TERMCRIT_ITER, 10, 1.0))

        cvZero( img )
        for i in range(sample_count):
            pt = points[i,0]
            cvCircle(img, cvPoint(cvRound(pt[0]), cvRound(pt[1])), 2, color_tab[clusters[i,0]], CV_FILLED, CV_AA, 0)
        
        cvShowImage( "clusters", img )

        if '%c' % (cvWaitKey(0) & 255) in ['\x1b','q','Q']: # 'ESC'
            break
