# -*- coding: utf-8 -*-

# MouseTrap
#
# Copyright 2009 Flavio Percoco Premoli
#
# This file is part of mouseTrap.
#
# MouseTrap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v2 as published
# by the Free Software Foundation.
#
# mouseTrap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mouseTrap.  If not, see <http://www.gnu.org/licenses/>.


"""Scripts Common Widgets Module."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import gtk
import cairo
import gobject
from gtk import gdk
from math import pi

BORDER_WIDTH = 0

# A quite simple gtk.Widget subclass which demonstrates how to subclass
# and do realizing, sizing and drawing.

class Mapper(gtk.Widget):

    def __init__(self, width, height):
        gtk.Widget.__init__(self)

        self.width   = width
        self.height  = height
        self.events  = { "motion" : [],
                         "click"  : []}
#         self._layout = self.create_pango_layout(text)
#         self._layout.set_font_description(pango.FontDescription("Sans Serif 16"))

    def do_realize(self):
        """
        Called when the widget should create all of its
        windowing resources.  We will create our gtk.gdk.Window
        and load our star pixmap.
        """

        # For some reason pylint says that a VBox doesn't have a set_spacing or pack_start member.
        # pylint: disable-msg=E1101
        # Mapper.do_realize: Class 'style' has no 'attach' member
        # Mapper.do_realize: Class 'style' has no 'set_background' member
        # Mapper.do_realize: Class 'style' has no 'fg_gc' member

        # First set an internal flag telling that we're realized
        self.set_flags(self.flags() | gtk.REALIZED)

        # Create a new gdk.Window which we can draw on.
        # Also say that we want to receive exposure events
        # and button click and button press events

        self.window = gdk.Window(
                self.get_parent_window(),
                width=self.allocation.width,
                height=self.allocation.height,
                window_type=gdk.WINDOW_CHILD,
                wclass=gdk.INPUT_OUTPUT,
                event_mask=self.get_events() | gdk.EXPOSURE_MASK
                        | gdk.BUTTON1_MOTION_MASK | gdk.BUTTON_PRESS_MASK
                        | gtk.gdk.POINTER_MOTION_MASK
                        | gtk.gdk.POINTER_MOTION_HINT_MASK)

        # Associate the gdk.Window with ourselves, Gtk+ needs a reference
        # between the widget and the gdk window
        self.window.set_user_data(self)

        # Attach the style to the gdk.Window, a style contains colors and
        # GC contextes used for drawing
        self.style.attach(self.window)

        # The default color of the background should be what
        # the style (theme engine) tells us.
        self.style.set_background(self.window, gtk.STATE_NORMAL)
        self.window.move_resize(*self.allocation)

        # self.style is a gtk.Style object, self.style.fg_gc is
        # an array or graphic contexts used for drawing the forground
        # colours
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        # pylint: enable-msg=E1101

        #self.connect("motion_notify_event", self.motion_notify_event)

    def do_unrealize(self):
        # The do_unrealized method is responsible for freeing the GDK resources

        # De-associate the window we created in do_realize with ourselves
        self.window.set_user_data(None)

    def do_size_request(self, requisition):
        # The do_size_request method Gtk+ is calling on a widget to ask
        # it the widget how large it wishes to be. It's not guaranteed
        # that gtk+ will actually give this size to the widget

        requisition.width  = self.width
        requisition.height = self.height

    def do_size_allocate(self, allocation):
        # The do_size_allocate is called by when the actual size is known
        # and the widget is told how much space could actually be allocated

        # Save the allocated space
        self.allocation = allocation

        # If we're realized, move and resize the window to the
        # requested coordinates/positions
        # pylint: disable-msg=W0142
        # Mapper.do_size_allocate: Used * or ** magic
        # WE DO NEED THE *
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)
        # pylint: enable-msg=W0142

    def expose_event(self, widget, event):
        """
        Mapper expose event.
        """
        # The do_expose_event is called when the widget is asked to draw itself
        # Remember that this will be called a lot of times, so it's usually
        # a good idea to write this code as optimized as it can be, don't
        # Create any resources in here.

#         x, y, self.width, self.height = self.allocation
#         self.draw_rectangle(BORDER_WIDTH,
#                             BORDER_WIDTH,
#                             self.width - 2*BORDER_WIDTH,
#                             self.height - 2*BORDER_WIDTH,
#                             self.style.fg[self.state],
#                             5.0)
#
#         w = self.width / 2
#         h = self.height / 2
#
#         self.draw_rectangle(60, 50, 80, 60, self.style.fg[self.state], 5.0)
#         self.draw_point( w + point.abs_diff.x, h - point.abs_diff.y, 2)

#         x, y, w, h = self.allocation
#         self.draw_rectangle(200,
#                             160,
#                             100,
#                             ,
#                             self.style.fg[self.state],
#                             5.0)
        return True

#         And draw the text in the middle of the allocated space
#         fontw, fonth = self._layout.get_pixel_size()
#         cr.move_to((w - fontw)/2, (h - fonth)/2)
#         cr.update_layout(self._layout)
#         cr.show_layout(self._layout)

    def draw_rectangle(self, x, y, width, height, color, line):
        """
        A Method to draw rectangles.
        """

        cr = self.window.cairo_create()
        cr.set_source_color(color)
        cr.rectangle(x, y, width, height)
        cr.set_line_width(line)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.stroke()

    def draw_point(self, X, Y, size, color = 'green'):
        """
        Draws the point

        Arguments:
        - self: The main object pointer.
        - X: The X possition.
        - Y: The Y possition
        - size: The point diameter.
        - color: A RGB color tuple. E.g (255,255,255)
        """

        cr = self.window.cairo_create()
        cr.set_source_rgb(0.7, 0.8, 0.1)
        cr.arc(X, Y, size, 0, 2 * pi)
        cr.fill_preserve()
        cr.stroke()

        return True

    def connect_point_event(self, event, x, y, width, height, callback):
        """
        Connects a new event in the spesified areas.

        Arguments:
        - self: The main object pointer.
        - event: The event type.
        - x: The x coord.
        - y: The y coord.
        - width: Event area width.
        - height: Event area height.
        - callback: The callback function.
        """

        if event not in self.events:
            return False

#         Working on Mapper events
#         self.events[event].append( {"x_range" : range(reg_event["x"], reg_event["x"] + reg_event["width"]),
#                                     "y_range" : range(reg_event["x"], reg_event["y"] + reg_event["height"]),
#                                     "callback" : callback} )

    def motion_notify_event(self, event):
        """
        Events
        """
        for reg_event in self.events["motion"]:
            if event.x in  reg_event["x_range"] and event.y in reg_event["y_range"]:
                reg_event["callback"]()


gobject.type_register(Mapper)
