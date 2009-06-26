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



""" Exposes mouseTrap as a DBus service for comunication purposes. """

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import dbus
import dbus.service
import mousetrap.debug as debug
from dbus.mainloop.glib import DBusGMainLoop

dbusserver = None
main_loop = DBusGMainLoop()
bus = dbus.SessionBus(mainloop=main_loop)

DBUS_NAME = "org.gnome.mousetrap"
DBUS_PATH = "/org/gnome/mousetrap"

# pylint: disable-msg=R0923
# Server: Interface not implemented

class DbusServer(dbus.service.Object):
    """DBus service"""

    def start( self ):
        """
        Initialize the dbus server module.

        Arguments:
        - lself: The main object pointer
        - mouseTrap: The mouseTrap onject pointer
        """

        bus_name = dbus.service.BusName(DBUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)

    @dbus.service.method(DBUS_NAME)
    def move(self, action):
        """
        Just Move the mouse to de required position.
        """
        print(action)
        #X, Y = action.split(",")
        #mouseTrap.move( "click", X, Y )

def start():
    """
    Start's the dbus server and store it in the global variable
    dbusserver, so it won't be started twice.
    """
    global dbusserver

    if dbusserver:
        return

    try:
        dbusserver = DbusServer()
        return True
    except:
        debug.exception( "mouseTrap.mTDbus", "The dbus server load failed" )


def shutdown():
    """
    Fake shutdown
    """
    pass
