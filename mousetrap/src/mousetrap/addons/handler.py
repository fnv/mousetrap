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

import os,re

class AddonsHandler(object):

    def __init__(self, controller):
        """
        This is the AddonsHandler init function

        Arguments:
        - self: The main object pointer.
        - controller: The mousetrap's controller.
        """

        self.ctr = controller

    def get_addons_list(self):
        """
        Checks the addons folder and gets the 
        list of present addons.

        Arguments:
        - self: The main object pointer.
        """
        
        reg = re.compile(r'([A-Za-z0-9]+)\.py$', re.DOTALL)
        dirname = os.path.dirname(__file__)
        return [ mod[0] for mod in [ reg.findall(f) for f in os.listdir("%s/" % dirname) if "handler" not in f] if mod ]

    def get_addon_inf(self, addon):
        """
        Gets basic information (Name, Description, Settings)

        Arguments:
        - self: The main object pointer.
        - addon: The addon to explore.
        """
        tmp = __import__("mousetrap.addons.%s" % addon,
                      globals(),
                      locals(),
                      [''])
        
        return { "name" : tmp.a_name, "dsc" : tmp.a_description, "stgs" : tmp.a_settings}

class AddonsBase(object):

    def __init__(self, controller):
        """
        This is the AddonsBase init function

        Arguments:
        - self: The main object pointer.
        - controller: The mousetrap's controller.
        """

        self.ctr = controller
        self.cfg = controller.cfg
        self.itf = self.ctr.itf

    def statusbar_message(self, msg):
        """
        Writes a message in the statusbar

        Arguments:
        - self: The main object pointer.
        - msg: The message.
        """
        self.itf.statusbar.push(self.itf.statusbar_id, msg)
    
    def add_item(self, item):
        """
        Adds any gtk widget to the addons vbox.

        Arguments:
        - self: The main object pointer.
        - item: The item to add.
        """
        self.itf.adds_vbox.pack_start(item, True, True)
