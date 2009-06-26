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

"""The mouse events handler."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import gtk
import pyatspi
import mousetrap.debug as debug
import mousetrap.environment as env
import Xlib.ext.xtest as xtest

from Xlib import X, display

clickVal  = { X.ButtonPress   : 0,
              X.ButtonRelease : 5 }

clickType = { 'p' : [ X.ButtonPress ],
              'r' : [ X.ButtonRelease ],
              'c' : [ X.ButtonPress, X.ButtonRelease],
              'd' : [ X.ButtonPress, X.ButtonRelease,
                      X.ButtonPress, X.ButtonRelease ] }


## GTK Display for any user
gtkDisplay = gtk.gdk.Display( "" )

## X Display for non gnome users
xDisplay   = display.Display()

isGnome = False
if env.desktop == "gnome":
    isGnome = True
    debug.debug( "mousetrap.mouse", "GNOME desktop has been detected" )

    ## pyatspi registry for gnome users
    reg = pyatspi.Registry

## Is the D&D click being used ?
dragging = False


def position( *arg ):
    """
    Get the absolute position of the mouse pointer

    Returns A list with the X and Y coordinates.
    """
    return list(gtkDisplay.get_pointer()[1:3])

def click( x = None, y = None, button = "bc1" ):
    """
    Execute Mouse Clicks. If the mouse is dragging an object
    then the release click will be performed.

    Arguments:
    - x: The X coordinate in the screen.
    - y: The Y coordinate in the screen.
    - button: The button click that has to be performed.

    Return True
    """

    global isGnome
    global dragging

    if not x or not y:
        x, y = position()

    if dragging:
        button = button[:2] + 'r'
        dragging = False
    elif button[2] == 'p':
        dragging = True

    if isGnome:
        try:
            reg.generateMouseEvent( x, y, button )
        except:
            isGnome = False
    else:
        for action in clickType[button[2]]:
            xDisplay.xtest_fake_input(action, int(button[1]), clickVal[action])
        xDisplay.flush()

    return True

def move( x=0, y=0, point=None ):
    """
    Changes the mouse position to the specified coords.

    Arguments:
    - self: The main object pointer.
    - x: The x position.
    - y: the y position.
    """
    global isGnome

    if point is not None:
        x, y = point.x, point.y

    if isGnome:
        try:
            reg.generateMouseEvent( x, y, 'abs' )
        except:
            isGnome = False
    else:
        xtest.fake_input( xDisplay, X.MotionNotify, x = x, y = y)
        #display.sync()
        xDisplay.flush()

    return True

###########################################
#               DEPRECATED
# Dictionary Dispatcher
# dsp = { "move"      : move,
#         "click"     : click,
#         "position"  : position }
#
# def handler( func ):
#     """
#     Mouse functions decorator.
#
#     Arguments:
#     - func: The function called to access the decorator.
#
#     Return The wrapper
#     """
#
#     def wrapper( *arg, **kw ):
#         """
#         Wrapper function.
#
#         This functions will execute the required function passing the arguments to it.
#
#         Return the function executed
#         """
#         return dsp[arg[0]]( *arg[1:], **kw )
#
#     return wrapper
