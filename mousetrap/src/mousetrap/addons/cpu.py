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

import os
import gobject
import mousetrap.debug as debug
import mousetrap.environment as env

from subprocess import Popen, PIPE
from mousetrap.addons.handler import AddonsBase

a_name = "CPU"
a_description = "Checks the CPU % usage"
a_settings = {}

class Addon(AddonsBase):

    def __init__(self, controller):
        AddonsBase.__init__(self, controller)
        
        gobject.timeout_add(1000, self.check_cpu)
        debug.debug("addon.cpu", "CPU addon started")

    def check_cpu(self):
        """
        Checks the CPU usage.

        Arguments:
        - self: The main object pointer.
        """
        cpu = (Popen("ps -e -o pcpu,pid | grep %s" % str(env.pid), shell=True, stdout=PIPE).stdout).read().strip().split(" ")[0]

        self.statusbar_message("CPU: %s" % cpu)
        return True
