"""Camshift calibration inerface"""

import gtk
import math
from ocvfw import pocv
from ctypes import c_int
from ctypesopencv import *
from ocvfw.dev.camera import Camera, Capture

class CalibrationGUI(gtk.Window):
	"""
	Class for the calibration gui
		
	Arugments:
		gtk.Window - GTK window object
	"""
	
	def __init__(self, controller):
		gtk.Window.__init__(self)
		
		# The MouseTrap controller object
		self.ctr = controller
		
		# The captured image
		self.cap_image = None
	
	
	def mask_gui(self):
		"""
		Defines the window for the mask
		"""
		
	def hist_gui(self):
		"""
		Defines the window for the histogram
		"""
		
	def cap_gui(self):
		"""
		Defines the window for the capture
		"""
		
		self.setWindowsIcon()
        self.set_title("Color Tracking Settings")
        self.connect("destroy", self.close)
        
        self.vBox = gtk.VBox()
        self.buttonsBox = gtk.HButtonBox()

        self.okButton = gtk.Button(stock = gtk.STOCK_OK)
        self.okButton.connect("clicked", self.finalizeSettings)
        self.buttonsBox.pack_start(self.okButton, True, True)
        
        self.applyButton = gtk.Button(stock = gtk.STOCK_APPLY)
        self.applyButton.connect("clicked", self.applySettings)
        self.buttonsBox.pack_start(self.applyButton, True True)
        
        self.closeButton = gtk.Button(stock = gtk.STOCK_CANCEL)
        self.closeButton.connect("clicked", self.close)
        self.buttonsBox.pack_start(self.closeButton, True True)
        
        self.vBox.pack_start(self.buttonsBox, True, True)
        
        
        self.cap_image = gtk.image()
        
        self.cap_expander = gtk.expander_new_with_mnemonic("Camera Image")
        self.cap_expander.add(self.cap_image)
        self.cap_expander.set_expanded(True)
		self.vBox.pack_start(self.cap_expander)
		
		self.vBox.show_all()
		self.add(self.vBox)
		self.show()
	
	def buildInterface(self):
		"""
		Build the Calibration GUI. Consists of the capture
        and a color selector
		"""
        
            

	def setWindowsIcon(self):
		"""
		Set the icon for the window
		"""
		icon_theme = gtk.icon_theme_get_default()
		try:
			icon = icon_theme.load_icon("mouseTrap", 48, 0)
		except:
			return
		
		gtk.window_set_default_icon(icon)
	
	def UpdateFrame(self, image):
		"""
		Updates the 
		
		Arguments:
			image - The image to display on the image frame
		"""
		

		if not image:
		    return False
    
		buff = gtk.gdk.pixbuf_new_from_data( img.imageData, gtk.gdk.COLORSPACE_RGB, False, 8, \
									int(img.width), int(img.height), img.widthStep )
		
		self.cap_image.set_from_pixbuf(buff)
		
    def _finalizeSettings(self):
    
    def _applySettings(self):       

def showCalibrationGui(controller):
	"""
	Shows the calibtation GUI
	
	Arguments:
		controller - The mousetrap object
	"""
	
	gui = CalibrationGUI(controller)
	gui.setWindowsIcon()
	gui.buildInterface()
    
