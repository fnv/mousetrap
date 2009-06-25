"""
	Main GUI object for our demo.
"""

import gtk

class GUI(gtk.Window):

	def __init__(self):
		
		gtk.Window.__init__(self)
	
	def setIcon(self):
		"""
		Try to set the application icon
		"""
		icon_theme = gtk.icon_theme_get_default()
		try:
			icon = icon_theme.load_icon("seaslug", 48, 0)
		except:
			return
		# Don't do anything for this exception but display the default.
		# We only care a little if there's no seaslugs
		gtk.window_set_default_icon(icon)
	
	def delete_event(self, widget, event, data=None):
		"""
		CB for the delete event
		"""
		return False
		
	def exit(self, widget, data=None):
		"""
		CB for exiting the program
		"""
		self.destroy()
			
	def buildUI(self):
		"""
		Builds the main GUI
		"""
		#self.setIcon()
		
		self.set_title( "Camshift Demo" )
		self.vBox = gtk.VBox()
		
		# This is the GTK image object that holds the capture data
		self.cap_image = gtk.Image()
		#self.cap_image.isVisible = True
		self.cap_image.set_from_file("timeline.jpg")
		self.cap_image.show()
		
		self.vBox.pack_start(self.cap_image)
		
		self.buttonsBox = gtk.HButtonBox()
		
		self.connect("delete_event", self.delete_event)
		
		self.quitButton = gtk.Button("Quit",stock=gtk.STOCK_QUIT)
		self.quitButton.connect("clicked", self.exit, None)
		self.quitButton.connect("clicked", gtk.Widget.destroy, self)
		self.buttonsBox.pack_start(self.quitButton, True, True)
		
		self.camToggleButton = gtk.Button("Show Camera")
		#self.camToggleButton.connect("clicked", self.toggleImgState)
		self.buttonsBox.pack_start(self.camToggleButton, True, True)
		
		self.vBox.pack_start(self.buttonsBox, False, False)

		self.vBox.show_all()
		
		# Add the vertical box to the window
		self.add(self.vBox)
		
		self.show()
		
	def toggleImgState(self, *args):
		"""
		Toggles whether the capture image is visible
		"""
		print "lol"
		#self.cap_image.isVisible = True if self.cap_image.isVisible == False else False
		
	def updateCapture(self, img):
		"""
		This function takes an IPLimage (or CVMat) and
		updates it. Used as a callback.
		"""
		
		if img is None:
			return False
		
		# Get the new gdk.pixbuf from the image data.
		# Pixbufs are objects containing a single image.
		buffer = gtk.gdk.pixbuf_new_from_data( img.imageData,
									       gtk.gdk.COLORSPACE_RGB,
									       False,
									       8,
									       int( img.width ),
									       int( img.height ),
									       img.widthStep )
		
		# Draw the pixbuf to the image GTK object
		self.cap_image.set_from_pixbuf(buffer)
	
	def main(self):
		gtk.main()