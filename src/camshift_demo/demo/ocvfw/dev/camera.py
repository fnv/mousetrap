# -*- coding: utf-8 -*-

# Ocvfw
#
# Copyright 2009 Flavio Percoco Premoli
#
# This file is part of Ocvfw.
#
# Ocvfw is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v2 as published
# by the Free Software Foundation.
#
# Ocvfw is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ocvfw.  If not, see <http://www.gnu.org/licenses/>>.


"""Camera Device Module."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import gobject

from warnings import *
from .. import debug
from opencv import cv
from opencv import highgui as hg
from .._ocv import Ocvfw as ocv


class __Camera(ocv):

    def init(self):
        """
        Initialize the camera.

        Arguments:
        - self: The main object pointer.
        - idx: The camera device index.
        - fps: The frames per second to be queried.
        - async: Enable/Disable asynchronous image querying. Default: False
        """
        self.idx = 0

    def set_camera(self, idx):
        self.idx = idx

    def start(self):
        self.start_camera(self.idx)


Camera = __Camera()


class Capture(object):

    def __init__(self, image=None, fps=100, async=False, idx=0):

        self.__lock        = False
        self.__flip        = {}
        self.__color       = "bgr"
        self.__props       = { "color" : "rgb" }
        self.__camera      = Camera
        self.__camera.set_camera(idx)
        self.__camera.start()

        self.__graphics    = { "rect"  : [],
                               "point" : []}

        self.__image       = image
        self.__image_log   = []
        self.__image_orig  = None

        color_vars         = [x for x in dir(cv) if '2' in x and str(getattr(cv, x)).isdigit()]
        self.__color_int   = dict(zip([x.lower() for x in color_vars], [getattr(cv,x) for x in color_vars]))

        self.roi           = None

        self.last_update   = 0
        self.last_duration = 0

        self.set_async(fps, async)

    def set_async(self, fps=100, async=False):
        """
        Sets/Unsets the asynchronous property.

        Arguments:
        - self: The main object pointer
        - fps: The frames per second to be queried.
        - async: Enable/Disable asynchronous image querying. Default: False
        """

        self.fps   = fps
        self.async = async

        if self.async:
            gobject.timeout_add(self.fps, self.sync)

    def sync(self):
        """
        Synchronizes the Capture image with the Camera image

        Arguments:
        - self: The main object pointer.
        """

        self.__camera.query_image()

        if not self.__image:
            self.__images_cn   = { 1 : cv.cvCreateImage ( self.__camera.imgSize, 8, 1 ),
                                   3 : cv.cvCreateImage ( self.__camera.imgSize, 8, 3 ),
                                   4 : cv.cvCreateImage ( self.__camera.imgSize, 8, 4 ) }

        self.__color       = "bgr"
        self.__image_orig  = self.__image = self.__camera.img

        if self.__color != self.__color_set:
            self.__image = self.color("rgb")

        # TODO: Workaround, I've to fix it
        if len(self.__camera.img_lkpoints["last"]) > 0:
            self.__camera.show_lkpoints()

        self.__camera.swap_lkpoints()

        self.show_rectangles(self.rectangles())

        self.__image = self.resize(200, 160)

        return self.async

    #@property
    def image(self):
        """
        Returns the image ready to use

        Arguments:
        - self: The main object pointer.
        """

        return self.__image

    def resize(self, width, height):
        """
        Image resizing function.

        Arguments:
        - self: The main object pointer.
        - width: The new image width.
        - height: The new image height.
        """

        tmp = cv.cvCreateImage( cv.cvSize( width, height ), 8, 3 )
        cv.cvResize( self.__image, tmp, cv.CV_INTER_AREA )
        return tmp


    def points(self):
        """
        Returns a list with the retangles that have been added.

        Arguments:
        - self: The main object pointer.
        """
        return self.__graphics["point"]

    def rectangles(self):
        """
        Returns a list with the retangles that have been added.

        Arguments:
        - self: The main object pointer.
        """
        return self.__graphics["rect"]

    def show_rectangles(self, rectangles):
        """
        Show the rectangles added.

        Arguments:
        - self: The main object pointer.
        """
        #debug.debug("Camera", "Showing existing rectangles -> %d" % len(rectangles))

        for rect in rectangles:
            cv.cvRectangle( self.__image, cv.cvPoint(rect.x, rect.y), cv.cvPoint(rect.size[0], rect.size[1]), cv.CV_RGB(255,0,0), 3, 8, 0 )

    def draw_point(self, x, y):
        cv.cvCircle(self.__image, [x,y], 3, cv.cvScalar(0, 255, 0, 0), -1, 8, 0)

    def original(self):
        """
        Returns an object with the original image.

        Arguments:
        -self: The main object pointer.
        """
        return Capture(self.__image_orig)

    def flip(self, flip):
        """
        Flips the image

        Arguments:
        - self: The main object pointer.
        - flip: Dictionary with keys "hor" and "ver" with values True/False.
        """

        if "hor" or "both" in flip:
            cv.cvFlip( self.__image, self.__image, 1)

        if "ver" or "both" in flip:
            cv.cvFlip( self.__image, self.__image, 0)

        return self.__image

    def color(self, new_color, channel=3):
        """
        Changes the image's color.

        Arguments:
        - self: The main object pointer.
        - color: The new color.

        returns self.color if color == None
        """

        if new_color:
            #img = cv.cvCreateImage ( cv.cvGetSize(self.__image), 8, channel )
            img = self.__images_cn[channel]
            cv.cvCvtColor( self.__image, img, self.__color_int['cv_%s2%s' % (self.__color, new_color) ])
            #cv.cvCvtColor( self.__image, img, self.__color_int['cv_%s2%s' % (self.__color, new_color) ])
            self.__color = new_color

        return img

    def change(self, size=None, color=None, flip=None):
        """
        Converts image properties.

        Arguments:
        - self: The main object pointer.
        - properties: The properties to change.
        """
        #self.__size     = size  if size  != None else self.__camera.imgSize
        self.__color_set = color if color.lower() != None else self.__color_set
        self.__flip      = flip  if flip  != None else self.__flip

    def add(self, graphic):
        """
        To add new objects to the capture image.

        Arguments:
        - self: The main object pointer.
        - graphic: The graphic object to add.
        """

        if self.is_locked():
            warn("The Capture is locked, no changes can be done", RuntimeWarning)
            return False

        if not hasattr(self, graphic.label):
            setattr(self, graphic.label, graphic)
            self.__graphics[graphic.type].append(graphic)

            if graphic.is_point():
                self.__camera.set_lkpoint(graphic)
        else:
            warn("The Graphic %s already exists. It wont be added" % graphic.label, RuntimeWarning)
            return False

    def remove(self, label=None):
        """
        Removes a graphic object.

        Arguments:
        - self: The main object pointer.
        - label: The graphic object label.
        """

        if self.is_locked():
            warn("The Capture is locked, no changes can be done", RuntimeWarning)
            return False

        if label is None:
            self.__graphics = []
        elif hasattr(self, label):
            del self.__graphics[self._graphics.index(getattr(self, label))]
            delattr(self, label)
        else:
            warn("The Graphic %s doesn't exists. Ignoring action" % label, RuntimeWarning)
            return False

    def get_area(self, haar_csd, roi=None, orig=None):
        """
        Gets an area using haarcascades. It is possible to get areas inside areas
        passing the roi rectangle and the origin point.

        Arguments:
        - self: the main object pointer.
        - haar_csd: The haartraining file
        - roi: The roi image coords if needed.
        - orig: The roi's origin if needed.
        """

        if roi is None:
            return self.__camera.get_haar_points(haar_csd)

        roi = cv.cvRect(roi["start"], roi["end"], roi["width"], roi["height"])
        return self.__camera.get_haar_roi_points(haar_csd, roi, orig)

    def message(self, message):
        """
        Adds a message to the image.

        Arguments:
        - self: The main object pointer.
        """
        pass

    def lock(self):
        """
        Locks The capture object. No change will b done.

        Arguments:
        - self: The main object pointer.
        """
        self.__lock = True

    def unlock(self):
        """
        Unlocks The capture object.

        Arguments:
        - self: The main object pointer.
        """
        self.__lock = False


    def is_locked(self):
        """
        Checks if the capture is locked

        Arguments:
        - self: The main object pointer.
        """
        return self.__lock


class Graphic(object):

    def __init__(self, type_, label, coords, size=None, color=None, parent=None, follow=None):
        """
        The new object initializer

        Arguments:
        - self: The main object pointer.
        - type_: The Graphic type.
        - label: The Graphic Object label.
        - coords: The Graphic Init coords list. E.g [X,Y]
        - size: The Graphic size list. E.g [Width, Height]
        - color: The Graphic rgb color tuple if needed.
        - parent: The parent class.
        - follow: The flow property is used for points. If True the optical flow will be enabled for this point.
        """

        self.parent   = parent

        self.x        = coords[0]
        self.y        = coords[1]
        self.size     = size
        self.type     = type_
        self.label    = label
        self.color    = color
        self.follow     = follow

    def is_point(self):
        """
        Checks if the graphic is a point.

        Arguments:
        - self: The main object pointer.

        returns True if the graphic is a point.
        """

        if self.type == "point":
            return True

        return False

class Point(Graphic):

    def __init__(self, type_, label, coords, size=None, color=None, parent=None, follow=None):
        Graphic.__init__(self, type_, label, coords, size, color, parent, follow)

        self.__ocv = None
        self.last  = None
        self.diff  = None
        self.orig  = cv.cvPoint( self.x, self.y )

    def set_opencv(self, opencv):
        """
        Sets the Graphic's opencv object.

        Arguments:
        - self: The main object pointer.
        - opencv: The opencv object.
        """

        # Update the current attrs
        self.x = opencv.x
        self.y = opencv.y

        if self.__ocv is not None:
            # Update the last attr
            self.last = self.__ocv

            # Update the diff attr
            self.rel_diff = cv.cvPoint( self.last.x - self.x,
                                        self.last.y - self.y )

            self.abs_diff = cv.cvPoint( self.x - self.orig.x,
                                        self.y - self.orig.y )

        self.__ocv = opencv


    @property
    def opencv(self):
        """
        Returns the Graphic opencv object

        Arguments:
        - self: The main object pointer.
        """
        return self.__ocv
