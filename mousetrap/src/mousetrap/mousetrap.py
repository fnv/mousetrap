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


"""MouseTrap's main script."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

####################### TAKEN FROM ORCA'S CODE ###################
# We're going to force the name of the app to "mousetrap" so pygtk
# will end up showing us as "mousetrap" to the AT-SPI.  If we don't
# do this, the name can end up being "-c".  See Orca's bug 364452 at
# http://bugzilla.gnome.org/show_bug.cgi?id=364452 for more
# information.
import sys
sys.argv[0] = "mousetrap"

import gobject
from ocvfw import pocv
from ui.main import MainGui
from ui.scripts.screen import ScriptClass
from lib import httpd, dbusd, settings

class Controller():
    """
    MouseTrap's Controller Class
    """

    def __init__(self):
        """
        The MouseTrap controller init class

        Arguments:
        - self: The main object pointer.
        """

        # We don't want to load the settings each time we need them. do we?
        self.cfg = None

        self.loop = gobject.MainLoop()
        self.httpd = httpd.HttpdServer(20433)
        self.dbusd = dbusd.DbusServer()


    def start(self):
        """
        Starts the modules, views classes.

        Arguments:
        - self: The main object pointer.
        """

        if self.cfg is None:
            self.cfg = settings.load()

        if not self.dbusd.start():
            self.httpd.start()

        if self.cfg.getboolean("main", "startCam"):
            # Lets start the module
            idm = pocv.get_idm(self.cfg.get("main", "algorithm"))
            self.idm = idm.Module(self)
            self.idm.set_capture(self.cfg.getint("cam", "inputDevIndex"))

            gobject.timeout_add(150, self.update_frame)
            gobject.timeout_add(50, self.update_pointers)

        # Lets build the interface
        self.itf = MainGui(self)
        self.itf.build_interface()
        self.itf.load_addons()

        gobject.threads_init()
        self.loop.run()

    def script(self):
        """
        Returns the main script class object.

        Arguments:
        - self: The main object pointer.
        """
        return ScriptClass()

    def update_frame(self):
        """
        Updates the User Interface frame with the latest capture.

        Arguments:
        - self: The main object pointer.
        """
        self.itf.update_frame(self.idm.get_image(), self.idm.get_pointer())
        return True

    def update_pointers(self):
        """
        Gets the new mouse pointer position based on the las calcs.

        Arguments:
        - self: The main object pointer.
        """
        self.itf.script.update_items(self.idm.get_pointer())
        return True
