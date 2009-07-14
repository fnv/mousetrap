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
from .. import commons as co
from ocvfw import _ocv as ocv

Camera = None

try:
    import gtk
except ImportError:
    debug.info("Camera", "Gtk not imported")

def _camera(backend):
    if not hasattr(ocv, backend):
        debug.warning("Camera", "Not such backend %s falling back to OcvfwPython" % backend)
        backend = "OcvfwPython"
    
    bknd = getattr(ocv, backend)

    @co.singleton
    class Camera(bknd):
        def __init__(self):
            bknd.__init__(self)

    return Camera()


class Capture(object):

    def __init__(self, image=None, fps=100, async=False, idx=0, backend="OcvfwPython"):

        global Camera

        self.__lock        = False
        self.__flip        = {}
        self.__color       = "bgr"
        self.__props       = { "color" : "rgb" }


        Camera = _camera(backend)
        Camera.set_camera_idx(idx)
        Camera.start_camera()
        debug.debug("Camera", "Loaded backend %s" % backend)

        self.__graphics    = { "rect"  : [],
                               "point" : []}

        self.__ch          = 3
        self.__image       = image
        self.__image_log   = []
        self.__image_orig  = None

        color_vars         = [x for x in dir(co.cv) if '2' in x and str(getattr(co.cv, x)).isdigit()]
        self.__color_int   = dict(zip([x.lower() for x in color_vars], [getattr(co.cv,x) for x in color_vars]))

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

        Camera.query_image()

        if not self.__image:
            self.__images_cn   = { 1 : co.cv.cvCreateImage ( Camera.imgSize, 8, 1 ),
                                   3 : co.cv.cvCreateImage ( Camera.imgSize, 8, 3 ),
                                   4 : co.cv.cvCreateImage ( Camera.imgSize, 8, 4 ) }

        self.__color       = "bgr"
        self.__image_orig  = self.__image = Camera.img

        if self.__color != self.__color_set:
            self.__image = self.color(self.__color_set)

        # TODO: Workaround, I've to fix it # We commented this out
        if len(Camera.img_lkpoints["last"]) > 0:
            Camera.show_lkpoints()

        if Camera.lk_swap():
            Camera.swap_lkpoints()

        self.show_rectangles(self.rectangles())

        return self.async

    def set_camera(self, key, value):
      """
      """
      Camera.set(key, value)

    #@property
    def image(self, new_img = None):
        """
        Returns the image ready to use

        Arguments:
        - self: The main object pointer.
        """

        if new_img:
            self.__image = new_img

        return self.__image

    def resize(self, width, height, copy=False):
        """
        Image resizing function.

        Arguments:
        - self: The main object pointer.
        - width: The new image width.
        - height: The new image height.
        """

        if self.__image is None:
            return False

        tmp = co.cv.cvCreateImage( co.cv.cvSize( width, height ), 8, self.__ch )
        co.cv.cvResize( self.__image, tmp, co.cv.CV_INTER_AREA )

        if not copy:
            self.__image = tmp

        return tmp

    def to_gtk_buff(self):
        """
        Converts image to gtkImage and returns it

        Arguments:
        - self: The main object pointer.
        """

        img = self.__image

        if "as_numpy_array" in dir(img):
            buff = gtk.gdk.pixbuf_new_from_array(img.as_numpy_array(), 
                                                 gtk.gdk.COLORSPACE_RGB, 
                                                 img.depth)
        else:
            buff = gtk.gdk.pixbuf_new_from_data(img.imageData, 
                                                gtk.gdk.COLORSPACE_RGB, False, 8,
                                                int(img.width), int(img.height), 
                                                img.widthStep )
        return buff

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
            co.cv.cvRectangle( self.__image, co.cv.cvPoint(rect.x, rect.y), co.cv.cvPoint(rect.size[0], rect.size[1]), co.cv.CV_RGB(255,0,0), 3, 8, 0 )

    def draw_point(self, x, y):
        co.cv.cvCircle(self.__image, [x,y], 3, co.cv.cvScalar(0, 255, 0, 0), -1, 8, 0)

    def original(self):
        """
        Returns an object with the original image.

        Arguments:
        -self: The main object pointer.
        """
        return Capture(self.__image_orig)

    def rect(self, *args):
        """
        Returns a Rectangle of the image.

        Arguments:
        - self: The main object pointer.
        - args: Could be the CVRect (at index 0) or the 4 values needed (X, Y, Width, Height)
        """

        if not self.__image:
            return

        rect = args[0]

        if len(args) > 1:
            rect = co.cv.cvRect( args[0], args[1], args[2], args[3] )

        return co.cv.cvGetSubRect(self.__image, rect)


    def flip(self, flip):
        """
        Flips the image

        Arguments:
        - self: The main object pointer.
        - flip: Dictionary with keys "hor" and "ver" with values True/False.
        """

        if "hor" or "both" in flip:
            co.cv.cvFlip( self.__image, self.__image, 1)

        if "ver" or "both" in flip:
            co.cv.cvFlip( self.__image, self.__image, 0)

        return self.__image

    def color(self, new_color, channel=None, copy=False):
        """
        Changes the image's color.

        Arguments:
        - self: The main object pointer.
        - color: The new color.

        returns self.color if color == None
        """

        channel = channel if channel != None else co.get_ch(new_color)

        if new_color:
            tmp = self.__images_cn[channel]
            co.cv.cvCvtColor( self.__image, tmp, self.__color_int['cv_%s2%s' % (self.__color, new_color) ])
            self.__color = new_color
            self.__ch = channel

        if not copy:
            self.__image = tmp

        return tmp

    def change(self, size=None, color=None, flip=None):
        """
        Converts image properties.

        Arguments:
        - self: The main object pointer.
        - properties: The properties to change.
        """
        #self.__size     = size  if size  != None else Camera.imgSize
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

            """if graphic.is_point():
                self.__camera.set_lkpoint(graphic) NEEDED?!?!?"""
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
            return Camera.get_haar_points(haar_csd)

        roi = cv.cvRect(roi["start"], roi["end"], roi["width"], roi["height"])
        return Camera.get_haar_roi_points(haar_csd, roi, orig)

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
        self.orig  = co.cv.cvPoint( self.x, self.y )

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
            self.rel_diff = co.cv.cvPoint( self.last.x - self.x,
                                        self.last.y - self.y )

            self.abs_diff = co.cv.cvPoint( self.x - self.orig.x,
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
