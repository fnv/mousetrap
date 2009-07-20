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


"""The Screen Mode script."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import mousetrap.environment as env
import mousetrap.lib.mouse as mouse
import mousetrap.lib.settings as settings

# pylint: disable-msg=F0401
# Unable to import 'widgets' (No module named widgets)
# Widgets is in the parent folder
from ..widgets import Mapper

from ocvfw import pocv

# The name given for the config file
setName = "screen"

## Internal Modes
modes = { "screen|abs"  :  "Mouse Absolute Movements",
          "screen|rel"  :  "Mouse Relative Movements"}



# We get too many E1101 messages, but We know what we're doing.
# Mapper does have those methods.
# pylint: disable-msg=E1101
class ScriptClass(Mapper):

    def __init__(self):
        Mapper.__init__(self, 200, 160)

        self.point       = None
        self.border_with = 0
        """
        self.threshold = 1 # Threshold for mouse movement.  If any mouse movement is 
                           # smaller than self.threshold pixels (I guess) then the mouse is not moved.
                           # Trying to reduce jitteriness. Not working.
        self.same_location_count = 0 # Yeah this variable name is bad.  It means the number of times
                                     # that the cursor has been in the same location under the threshold.
        """
        self.connect("expose_event", self.expose_event)
        
        self.cfg = settings.load()
    
        algorithm_info = pocv.get_idm_inf("color")
        
        if(algorithm_info["name"] == "color"):
            self.scale = self.cfg.get("color", "vscale")
        elif ( algorithm_info["name"] == "forehead"):
            self.scale = self.cfg.get("forehead", "vscale")
            

    def update_items(self, point):
        self.point = point
        #self.point.set_opencv(self.point)
        self.calc_move()
        self.queue_draw()

    def expose_event(self, widget, event):
        self.width, self.height = self.allocation[2], self.allocation[3]

        self.draw_rectangle(self.border_with,
                            self.border_with,
                            self.width - 2*self.border_with,
                            self.height - 2*self.border_with,
                            self.style.fg[self.state],
                            5.0)

        self.center = { "x" : self.width / 2,
                        "y" : self.height / 2 }

        #we need to figure out how to get access to the cfg file from here
        self.vscreen = { "x" : self.center["x"] - int(self.scale) * 4 / 2,
                         "y" : self.center["y"] - int(self.scale) * 3 / 2,
                         "width"  : int(self.scale) * 4,
                         "height" : int(self.scale) * 3}

        self.draw_rectangle( self.vscreen["x"], self.vscreen["y"],
                             self.vscreen["width"], self.vscreen["height"],
                             self.style.fg[self.state], 5.0)

        if hasattr(self.point, "abs_diff"):
            self.vpoint = { "x" : self.center["x"] - self.point.abs_diff.x,
                            "y" : self.center["y"] + self.point.abs_diff.y }

            self.draw_point( self.vpoint["x"], self.vpoint["y"], 2)

    def calc_move(self):
        if not hasattr(self, "vpoint"):
            return False

        x, y = mouse.position()
        """
        # If the difference between the new point and the last point is less than the threshold:
        if -self.threshold < self.point.rel_diff.x < self.threshold or -self.threshold < self.point.rel_diff.y < self.threshold:
            self.same_location_count+=1
            # If the point has been in the same location for more than 5 frames:
            if self.same_location_count > 5:
                mouse.move(x,y) # Leave the mouse in the same location
                return False
        """
        par = ["width", "height"]

        new_x, new_y = [ (float(poss)/self.vscreen[par[i]])*env.screen[par[i]]
                      for i,poss in enumerate([ (self.vscreen["width"]/2) - ( self.center["x"] - self.vpoint["x"]),
                                                (self.vscreen["height"]/2) - ( self.center["y"] - self.vpoint["y"] ) ])]

        mouse.move( new_x, new_y)
        #mouse.move(self.point.x, self.point.y)

    def prefferences(self):
        """
        This function contains the screen's script prefferences dialog tab.

        Arguments:
        - self: the main object pointer.
        """
        pass
