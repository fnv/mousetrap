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
		
		self.ctr = controller
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
	
	def buildInterface(self):
		"""
		Build the Calibration GUI
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
	
	def Ipl_to_Gtk(self, image):
		

def showCalibrationGui(controller):
	"""
	Shows the calibtation GUI
	
	Arguments:
		controller - The mousetrap object
	"""
	
	gui = CalibrationGUI(controller)
	gui.setWindowsIcon()
	gui.buildInterface()
    
