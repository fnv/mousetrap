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

""" A group of formated dialogs functions used by mousetrap. """

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Flavio Percoco Premoli"
__license__   = "GPLv2"

import gtk
from i18n import _

def addLabelMessage( dialog, message ):
    """
    Adds a label to the dialog

    Arguments:
    - dialog: The dialog object pointer.
    - message: The dialog message
    """

    label = gtk.Label()
    label.set_use_markup(True)
    label.set_markup('<span>' + \
        message + "</span>")
    label.show()
    dialog.hbox.pack_start(label)

def addImage( dialog, stockImage, stock=False):
    """
    Adds an image to a dialog.

    Arguments:
    - dialog: The dialog object pointer.
    - stockImage: The image to set.
    - stock. is it a stock image? False if it isn't.
    """

    image = gtk.Image()
    if stock:
        image.set_from_stock( stockImage, gtk.ICON_SIZE_DIALOG )
    else:
        pass
    image.set_alignment( 0.0, 0.5 )
    image.show()
    dialog.hbox.pack_start(image)

def confirmDialog( message, parent ):
    """
    Creates a confirmation dialog.

    Arguments:
    - message: The dialog message
    - parent: The parent window. None if there's not one.
    """

    dialog = createDialog( _( "Confirmation Dialog" ), parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, \
                            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    addImage( dialog, gtk.STOCK_DIALOG_WARNING, True)
    addLabelMessage( dialog, message )
    return dialog.run()

def errorDialog( message, parent ):
    """
    Creates an error dialog using the messageDialog function.

    Arguments:
    - message: The dialog message
    - parent: The parent window. None if there's not one.
    """
    return messageDialog( _("Error Dialog"), message, parent,  gtk.STOCK_DIALOG_ERROR )

def warningDialog( message, parent ):
    """
    Creates a warning dialog using the messageDialog function.

    Arguments:
    - message: The dialog message
    - parent: The parent window. None if there's not one.
    """
    return messageDialog( _("Information Dialog"), message, parent,  gtk.STOCK_DIALOG_WARNING )

def informationDialog( message, parent ):
    """
    Creates an information dialog using the messageDialog function.

    Arguments:
    - message: The dialog message
    - parent: The parent window. None if there's not one.
    """
    return messageDialog( _("Information Dialog"), message, parent,  gtk.STOCK_DIALOG_INFO )

def messageDialog( title, message, parent, stockImage, stock = True ):
    """
    Creates a simple message dialog. E.g: Error, Warnings, Informations.

    Arguments:
    - title: The dialog title.
    - message: The dialog message.
    - parent: The parent Window, None if there's not one.
    - stockImage: The image to show.
    - stock: If the image is a stock image.
    """
    dialog = createDialog( title, parent, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

    addImage( dialog, stockImage, stock)
    addLabelMessage( dialog, message )
    return dialog.run()

def closeDialog( dialog, *args ):
    """
    Close Function for dialogs.

    Arguments:
    - dialog: the dialog to destroy.
    - *args: The widget event arguments.
    """
    dialog.destroy()

def createDialog( title, parent, flags, buttons ):
    """
    Creates a Dialog Window.

    Arguments:
    - self: The main object pointer.
    - title: The Dialog window Title
    - parent: The parent window.
    - message: A message to show in the dialog.
    - stockImage: A GTK+ stock image.
    - flags: gtk.Dialog Flags to set the typo of dialog. E.g: gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
    - buttons: A tuple with the gtk.Buttons to show. E.g: ( gtk.STOCK_OK, gtk.STOCK_CANCEL )
    """

    # For some reason pylint says that a VBox doesn't have a set_spacing or pack_start member.
    # pylint: disable-msg=E1101
    # createDialog: Class 'vbox' has no 'set_spacing' member
    # createDialog: Class 'vbox' has no 'pack_start' member
    dialog = gtk.Dialog( title, parent, flags, buttons )
    dialog.set_default_size(150, 100)
    dialog.set_position(gtk.WIN_POS_CENTER)
    dialog.set_border_width(8)
    dialog.vbox.set_spacing ( 4 )

    hbox = gtk.HBox(spacing=4)

    #bbox = gtk.HButtonBox()
    #bbox.set_spacing(4)
    #bbox.set_layout(gtk.BUTTONBOX_END)

    dialog.vbox.pack_start(hbox, True, True)
    # pylint: enable-msg=E1101
    # createDialog: Class 'vbox' has no 'set_spacing' member
    # createDialog: Class 'vbox' has no 'pack_start' member

    #vbox.pack_start(bbox, False)

    #dialog.add(vbox)

    #setattr(dialog, 'vbox', vbox)
    setattr(dialog, 'hbox', hbox)
    #setattr(dialog, 'bbox', bbox)

    #args = list(args)
    #args.insert(0, stock.CLOSE)
    dialog.connect('delete-event', closeDialog, dialog)

    dialog.show_all()
    return dialog

class IdmSettings(gtk.Window):

    def __init__(self, cfg, name, stgs):
        """
        Idm Settings window.

        Arguments:
        self: The main object pointer.
        cfg: The config object.
        stgs: The idm's settings dict to parse.
        """
        gtk.Window.__init__(self)

        self.cfg = cfg
        self.idm_stgs = eval(stgs)
        self.idm = name.lower()
        self.tmp = {}

        #self.set_size_request( 500 , 120)
        #self.set_default_size( 500 , 120)
        self.set_title(_("%s Config's Dialog" % self.idm.capitalize()))

        self.main_vbox = gtk.VBox(spacing=6)
        self.add_widgets()

        buttons_box = gtk.HBox(spacing=6)

        button = gtk.Button( _("Accept"), stock=gtk.STOCK_OK )
        button.connect("clicked", self.accept_button)
        buttons_box.pack_start(button, False, False)

        button = gtk.Button( _("Cancel"), stock=gtk.STOCK_CANCEL )
        button.connect("clicked", self.cancel_button)
        buttons_box.pack_start(button, False, False)

        buttons_box.show_all()

        self.main_vbox.pack_start(buttons_box, False, False)

        self.main_vbox.show_all()
        self.show_all()
        self.add(self.main_vbox)

        if not self.cfg.has_section(self.idm):
            self.cfg.add_section(self.idm)

    def accept_button(self, widget, *args):
        for key in self.tmp:
            self.cfg.set(self.idm, key, self.tmp[key])
        self.destroy()

    def cancel_button(self, widget, *args):
        self.destroy()

    def add_widgets(self):
        """
        Adds dinamicaly the widgets to the dialog.

        Arguments:
        - self: The main object pointer.
        """
        for key in self.idm_stgs:
            self.main_vbox.pack_start(self.create_labled_input(key), False, False)

    def value_changed(self, widget, key):
        self.tmp[key] = widget.get_text()

    def create_labled_input(self, key):
        """
        Creates a textbox with a lable.

        Arguments:
        - self: The main object pointer.
        - key: The parent key.
        """
        hbox = gtk.HBox()
        label = gtk.Label(_(key.capitalize()))
        label.set_use_underline( True )
        label.show()
        hbox.pack_start(label, True, True)

        val = str(self.idm_stgs[key]["value"])
        if self.cfg.get(self.idm, key):
            val = self.cfg.get(self.idm, key)

        entry = gtk.Entry()
        entry.set_text(val)
        entry.connect("changed", self.value_changed, key)
        entry.show()
        hbox.pack_start(entry, True, True)
        hbox.show_all()
        return hbox

###############################################
#                                             #
#    THE WHEEL HAS ALREADY BEEN DISCOVERED    #
#     SO, LETS USE MOUSETWEAK INSTEAD OF      #
#      ADD THIS SUPPORT TO MOUSETRAP.         #
###############################################
# class ClicksDialog( gtk.Window ):
#     """
#     A Class for the Click Dialog.
#
#     Arguments:
#     - gtk.Window: Window for the buttons.
#     """
#
#     def __init__( self, gui ):
#         """
#         Initialize the Clicks Dialog.
#
#         Arguments:
#         - self: The main object pointer.
#         - mouseTrap: The mouseTrap object pointer.
#         - cAm: The camera object pointer
#         """
#
#         gtk.Window.__init__( self )
#
#         self.gui = gui
#
#         self.set_property("skip-taskbar-hint", True)
#         self.set_keep_above( True )
#         self.set_size_request( 500 , 120)
#         self.set_default_size( 500 , 120)
#         self.width, self.height = self.get_default_size()
#
#         self.set_title(_('Clicks Panel'))
#
#         self.set_app_paintable(True)
#         #self.set_decorated(False)
#
#         self.buttons = []
#         self.blue  = '#1161d9'
#         self.green = '#60da11'
#         evtBox = gtk.EventBox()
#
#         buttonsBox = gtk.HBox( spacing = 6 )
#         buttonsBox.show_all()
#
#         self.leftClick = gtk.Button()
#         self.leftClick.add(self._newImageButton(_("Left Click"),
#                                                   "%s/images/leftClick.png" % env.mTDataDir))
#         self.leftClick.connect("clicked", self.executeClick, 'b1c')
#         self.leftClick.show()
#         self.buttons.append( self.leftClick )
#         buttonsBox.pack_start( self.leftClick )
#
#         self.doubleClick = gtk.Button()
#         self.doubleClick.add(self._newImageButton(_("Double Click"),
#                                                     "%s/images/doubleClick.png" % env.mTDataDir))
#         self.doubleClick.connect("clicked", self.executeClick, 'b1d')
#         self.doubleClick.show()
#         self.buttons.append( self.doubleClick )
#         buttonsBox.pack_start( self.doubleClick )
#
#         self.leftHold = gtk.Button()
#         self.leftHold.add(self._newImageButton(_("Drag/Drop Click"),
#                                                  "%s/images/leftHold.png" % env.mTDataDir))
#         self.leftHold.connect("clicked", self.executeClick, 'b1p')
#         self.leftHold.show()
#         self.buttons.append( self.leftHold )
#         buttonsBox.pack_start( self.leftHold )
#
#         #~ self.middleClick = gtk.Button()
#         #~ self.middleClick.add(self._newImageButton(_("Middle Click"), "%s/images/middleClick.png" % env.mTDataDir))
#         #~ self.middleClick.connect("clicked", self.executeClick, 'b2c')
#         #~ self.middleClick.show()
#         #~ self.buttons.append( self.middleClick )
#         #~ buttonsBox.pack_start( self.middleClick )
#
#         self.rightClick = gtk.Button()
#         self.rightClick.add(self._newImageButton(_("Right Click"),
#                                                    "%s/images/rightClick.png" % env.mTDataDir))
#         self.rightClick.connect("clicked", self.executeClick, 'b3c')
#         self.rightClick.show()
#         self.buttons.append( self.rightClick )
#         buttonsBox.pack_start( self.rightClick )
#
#         self.add( buttonsBox  )
#
#     def showPanel( self ):
#         """
#         Shows the panel
#
#         Arguments:
#         - self: The main object pointer.
#         """
#
#         X = Y = 0
#
#         poss = mouseTrap.mice( "position" )
#
#         # We'll change the click panel position to be sure that
#         # it won't appear under another window or worse under a
#         # popup menu.
#         if poss[0] in xrange( env.screen["width"]/2 ):
#             X = env.screen["width"] - self.width
#
#
#         if poss[1] in xrange( env.screen["height"]/2 ):
#             Y = env.screen["height"] - self.height
#
#
#         self.move(X, Y)
#
#         if self.get_focus():
#             self.buttons[ self.buttons.index(self.get_focus()) ].get_child().modify_bg( gtk.STATE_NORMAL,
#                                                                                         gtk.gdk.color_parse(self.blue))
#
#         self.set_focus(self.buttons[0])
#         self.buttons[0].get_child().modify_bg( gtk.STATE_NORMAL, gtk.gdk.color_parse(self.green))
#         self.show_all()
#
#         mouseTrap.setState( "clk-dialog" )
#
#     def hidePanel( self, *args ):
#         """
#         Hides the panel
#
#         Arguments:
#         - self: The main object pointer.
#         - args: The event arguments
#         """
#         self.hide()
#         mouseTrap.setState( "active" )
#
#     def pressButton( self, *args ):
#         """
#         Press the focused button
#
#         Arguments:
#         - self: The main object pointer.
#         - args: The event arguments
#         """
#
#         self.get_focus().clicked()
#
#     def prevBtn( self, *args ):
#         """
#         Move to the prev button
#
#         Arguments:
#         - self: The main object pointer.
#         - args: The event arguments
#         """
#
#         self.buttons[ self.buttons.index(self.get_focus()) ].get_child().modify_bg( gtk.STATE_NORMAL,
#                                                                                     gtk.gdk.color_parse(self.blue))
#         self.buttons[ self.buttons.index(self.get_focus()) - 1 ].grab_focus()
#         self.buttons[ self.buttons.index(self.get_focus()) ].get_child().modify_bg( gtk.STATE_NORMAL,
#                                                                                     gtk.gdk.color_parse(self.green))
#
#     def nextBtn( self, *args ):
#         """
#         Move to the next button
#
#         Arguments:
#         - self: The main object pointer.
#         - args: The event arguments
#         """
#
#         index = self.buttons.index(self.get_focus()) + 1
#         if index >= len(self.buttons):
#             index = 0
#         self.buttons[ index -1 ].get_child().modify_bg( gtk.STATE_NORMAL,
#                                                         gtk.gdk.color_parse(self.blue))
#         self.buttons[ index ].grab_focus()
#         self.buttons[ index ].get_child().modify_bg( gtk.STATE_NORMAL,
#                                                      gtk.gdk.color_parse(self.green))
#
#     def executeClick( self, widget, button ):
#         """
#         Execute the selected click
#
#         Arguments:
#         - self: The main object pointer.
#         - widget: The button clicked.
#         - button: The mouse button that should be pressed.
#         """
#
#         self.gui.clickDlgHandler( button )
#         self.hidePanel()
#
#     def _newImageButton( self, label, image ):
#         """
#         Creates an image button from an image file
#
#         Arguments:
#         - self: The main object pointer
#         - label: The buttons label
#         - image: The image path
#
#         Returns ButtonLabelBox A gtk.HBox that contains the new image stock button.
#         """
#         evt = gtk.EventBox()
#
#         buttonLabelBox = gtk.VBox()
#
#         im = gtk.Image()
#         im.set_from_file( image )
#         im.show
#
#         label = gtk.Label( label )
#         label.set_alignment( 0.0, 0.5 )
#         label.set_use_underline( True )
#
#         buttonLabelBox.pack_start( im )
#         buttonLabelBox.pack_start( label )
#         buttonLabelBox.show_all()
#
#         evt.add(buttonLabelBox)
#         evt.modify_bg( gtk.STATE_NORMAL, gtk.gdk.color_parse(self.blue))
#         evt.modify_bg( gtk.STATE_PRELIGHT, gtk.gdk.color_parse(self.green))
#         return evt


class CairoTransGui( gtk.Window ):

    def __init__( self, message ):
        gtk.Window.__init__(self)

        self.set_property("skip-taskbar-hint", True)
        self.connect("expose-event", self.expose)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.clicked)
        self.set_size_request( 700 , 100)
        #self.connect('screen-changed', self.screenChanged)

        self.set_title('MouseTrap Message!!!')


        self.set_app_paintable(True)
        self.set_decorated(False)

        self.message = message

        self.show_all()

    def expose( self, widget, event):

        cr = widget.window.cairo_create()

        cr.set_operator(1)
        cr.paint()

        cr.set_source_rgba (255.0, 255.0, 255.0, 100.0)
        cr.set_font_size (50)
        cr.move_to (0, 70)
        cr.show_text (self.message)
        cr.fill()
        cr.stroke()
        return False

    def clicked(self, widget, event):
        #If a shift key is pressed, start resizing
        self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

