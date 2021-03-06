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


"""The main GUI of mousetrap."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import gtk
import dialogs
import settings_gui
import colorsys
import mousetrap.debug as debug
import mousetrap.environment as env
from ocvfw import pocv
from mousetrap.addons import cpu

class MainGui( gtk.Window ):
    """
    MouseTrap main GUI Class
    """

    def __init__( self, controller ):
        """
        The main GUI constructor

        Arguments:
        - self: The main object pointer
        - controller: The mouseTrap's controller.
        """

        gtk.Window.__init__( self )
        self.ctr    = controller
        self.cfg    = controller.cfg
        self.script = self.ctr.script()
        #self.set_default_size(200, 400)

    def setWindowsIcon( self ):
        """
        Sets the mainGui icon

        Arguments:
        - self: The main object pointer
        """

        icon_theme = gtk.icon_theme_get_default()
        try:
            icon = icon_theme.load_icon("mousetrap", 48, 0)
        except:
            return

        gtk.window_set_default_icon(icon)

    def handleKeyboardInput( self, window, event ):
        """
        Callback to handle custom keyboard shortcuts.
        
        Arguments:
        - self: The main object pointer
        - window: The GTK Window object where the event happened
        - event: The GDK event containing relevant event data
        """
        
        if not hasattr(self.ctr, "idm"):
            return
        
        key = event.string
        alg_inf = pocv.get_idm_inf("color")
        
        
        
        # Right now this only works for the color idm. Maybe
        # all idms should have a standard method to stop and start
        # tracking?
        
        if(alg_inf["name"]== "color"):
            if (key == 't'):
                try:
                    self.ctr.idm.startTracking()
                except ValueError:
                    print 'The selection height/width are invalid.'
            elif (key == 'x'):
                if not hasattr(self.ctr, "idm"):
                    return
                    
                self.ctr.idm.stopTracking()
            elif (key == 'm'):
                if not hasattr(self.ctr, "idm"):
                    return
                
                self.ctr.idm.selSizeUp()
            elif (key == 'n'):
                if not hasattr(self.ctr, "idm"):
                    return

                self.ctr.idm.selSizeDown()
            elif (key == 'w'):
                if not hasattr(self.ctr, "idm"):
                    return
                self.ctr.idm.selPositionUp()
            elif (key == 'a'):
                if not hasattr(self.ctr, "idm"):
                    return
                self.ctr.idm.selPositionLeft()
            elif (key == 's'):
                if not hasattr(self.ctr, "idm"):
                    return
                self.ctr.idm.selPositionDown()
            elif (key == 'd'):
                if not hasattr(self.ctr, "idm"):
                    return
                self.ctr.idm.selPositionRight()


    def build_interface( self ):
        """
        Builds the interface

        Arguments:
        - self: The main object pointer
        """
        self.connect("key-press-event", self.handleKeyboardInput)
        self.set_resizable(False)

        self.setWindowsIcon()

        accelGroup = gtk.AccelGroup()
        self.add_accel_group( accelGroup )

        self.accelGroup = accelGroup
        
        self.add_events(gtk.gdk.KEY_PRESS_MASK)

        self.set_title( "MouseTrap" )
        self.connect( "destroy", self.close)
        self.setWindowsIcon()

        self.vBox = gtk.VBox()

        self.buttonsBox = gtk.HButtonBox()
        #self.buttonsBox = gtk.HBox(False,0)

        self.prefButton = gtk.Button(stock=gtk.STOCK_PREFERENCES)
        self.prefButton.connect("clicked", self._show_settings_gui)
        self.buttonsBox.pack_start( self.prefButton, True, True )

        self.closeButton = gtk.Button(stock=gtk.STOCK_QUIT)
        self.closeButton.connect("clicked", self.close)
        self.buttonsBox.pack_start( self.closeButton, True, True )

        self.helpButton = gtk.Button(stock=gtk.STOCK_HELP)
        self.helpButton.connect("clicked", self._loadHelp)
        self.buttonsBox.pack_start( self.helpButton, True, True )

        self.vBox.pack_start( self.buttonsBox, False, False )

        self.adds_vbox = gtk.VBox()
        self.adds_vbox.show_all()
        self.vBox.pack_start( self.adds_vbox, False, False )

        self.cap_image    = gtk.Image()

        if self.cfg.getboolean("gui", "showCapture"):
            self.cap_expander = gtk.expander_new_with_mnemonic("_Camera Image")
            self.cap_expander.add(self.cap_image)
            #expander.connect('notify::expanded', self.expanded_cb)          
            self.cap_expander.set_expanded(True)
            self.vBox.pack_start(self.cap_expander)
            
            
            if self.cfg.get("main", "algorithm") == "color":
                self.pal_expander = gtk.expander_new_with_mnemonic("Color _Picker")
                # Create a vertical box inside the color picker expander for layout
                self.pickerBox = gtk.VBox(spacing=10)
                
                
                self.picker = gtk.ColorSelection()
                self.picker.set_has_palette(True)
                self.pickerBox.pack_start(self.picker)
                
                self.saveColorButton = gtk.Button(stock=gtk.STOCK_SAVE)
                self.saveColorButton.connect("clicked", self._changeColors)
                
                # Weird config file hack. See Module.update_hue_range() docs
                if self.cfg.getboolean("main", "startCam"):
                    self.saveColorButton.connect("clicked", self.ctr.idm.update_hue_range)
                
                self.pickerBox.pack_start(self.saveColorButton)
                
                self.pal_expander.add(self.pickerBox)
                
                self.vBox.pack_start(self.pal_expander)

        if self.cfg.getboolean("gui", "showPointMapper"):
            self.map_expander = gtk.expander_new_with_mnemonic("_Script Mapper")
            self.map_expander.add(self.script)
            self.map_expander.set_expanded(True)
            #expander.connect('notify::expanded', self.expanded_cb)
            self.vBox.pack_start(self.map_expander)

#
#         flipButton = gtk.Button( _("Flip Image") )
#         flipButton.connect("clicked", self.recalcPoint, "flip" )
#         hBox.pack_start( flipButton, False, False )
#
#         recalcButton = gtk.Button( _("Recalc Point") )
#         recalcButton.connect("clicked", self.recalcPoint )
#         hBox.pack_start( recalcButton, False, False )
#
#         self.vBox.pack_end(hBox, False, False )
#
#         self.buttonsBox.show_all()

        self.statusbar = gtk.Statusbar()
        self.statusbar_id = self.statusbar.get_context_id("statusbar")

        self.vBox.pack_start(self.statusbar, True, True)

        self.vBox.show_all()
        self.add(self.vBox)
        self.show()

        debug.debug("ui.main", "Interface Built")

    def load_addons(self):
        """
        Loads the enabled addons
         
        Arguments:
        - self: The main object pointer.
        """

        for add in self.cfg.getList("main", "addon"):
            tmp = __import__("mousetrap.addons.%s" % add,
                    globals(), locals(),[''])

            setattr(self, add, tmp.Addon(self.ctr))
        debug.debug("ui.main", "Addons loaded")


    def update_frame(self, cap, point):
        """
        Updates the image

        Arguments:
        - self: The main object pointer.
        - img: The IPLimage object.
        """

        if not cap.image():
            return False

        #self.script.update_items(point)
        """buff = gtk.gdk.pixbuf_new_from_data( img.imageData, gtk.gdk.COLORSPACE_RGB, False, img.depth, \
                                             int(img.width), \
                                             int(img.height), \
                                             img.widthStep ) 

        buff = gtk.gdk.pixbuf_new_from_array(img.as_numpy_array(), gtk.gdk.COLORSPACE_RGB, img.depth)

        #sets new pixbuf
        self.cap_image.set_from_pixbuf(buff)"""

        #sets new pixbuf -- Flavio's new way, untested
        self.cap_image.set_from_pixbuf(cap.to_gtk_buff().scale_simple(200, 160, gtk.gdk.INTERP_BILINEAR))

#     def recalcPoint( self, widget, flip = ''):
#         """
#         Enables the Flip of the Image in the X axis
#
#         This is for webcams that capture images as a mirror.
#
#         Arguments:
#         - self: The main object pointer.
#         - *args: Widget related arguments.
#         """
#
#         if flip:
#             self.settings.set( "cam", "flipImage",  str(not self.settings.getboolean( "cam", "flipImage" )) )
#
#         mouseTrap.calcPoint()
#

    def _newStockImageButton( self, label, stock ):
        """
        Creates an image button from gtk's stock.

        Arguments:
        - self: The main object pointer
        - label: The buttons label
        - stock: The Stock image the button will use. E.g: gtk.STOCK_GO-FORWARD

        Returns buttonLabelBox A gtk.HBox that contains the new image stock button.
        """

        buttonLabelBox = gtk.VBox()

        im = gtk.image_new_from_stock( stock, gtk.ICON_SIZE_BUTTON )

        label = gtk.Label( label )
        #label.set_alignment( 0.0, 0.5 )
        label.set_use_underline( True )

        buttonLabelBox.pack_start( im )
        buttonLabelBox.pack_start( label )
        buttonLabelBox.show_all()

        return buttonLabelBox

    def _show_settings_gui( self, *args ):
        """
        Starts the preferences GUI

        Arguments:
        - self: The main object pointer.
        - *args: The widget callback arguments.
        """

        settings_gui.showPreffGui(self.ctr)
        
    def _changeColors(self, *args):
        """
        Updates the configuration file with the new color values
        """
        color = self.picker.get_current_color()
        
        # Note: This is reversed (GBR), but it's written to the config file as RGB.
        # This is because ConfigParser.set presumably places these on a stack before
        # they are written. If called in RGB order, they are written as BGR.
        self.cfg.set("color", "blue", str(color.blue))
        self.cfg.set("color", "green", str(color.green))
        self.cfg.set("color", "red", str(color.red))
        
        self._finalizeConfigChanges()
    
    def _loadHelp( self, *args ):
        """
        Shows the user manual.

        Arguments:
        - self: The main object pointer.
        - *args: The widget callback arguments.
        """

        try:
            import gnome
            gnome.help_display_uri("ghelp:%s/docs/mousetrap.xml" % env.mTDataDir)
        except ImportError:
            dialogs.errorDialog(
            "mouseTrap needs <b>gnome</b> module to show the help. Please install gnome-python and try again.", None )
            debug.exception( "mainGui", "The help load failed" )

    def _finalizeConfigChanges(self):
        """
        Writes to the config file any changes that have been made..
        """
        self.cfg.write(open(env.configPath + "userSettings.cfg", "w"))
        
    def close( self, *args ):
        """
        Close Function for the quit button. This will kill mouseTrap.

        Arguments:
        - self: The main object pointer.
        - *args: The widget callback arguments.
        """
        exit()
        #self.mTp.quit(0)

def showMainGui( ):
    """
    Loads the mainGUI components and launch it.

    Arguments:
    - mouseTrap: The mouseTrap object pointer
    """

    gui = MainGui()
    gui.build_interface()
    return gui

