import sys
import gobject
import ocvfw.idm.camshift as camshift
from ui.main import GUI

class Controller():
	"""
	Main controller class
	"""
	
	def __init__(self):
		self.loop = gobject.MainLoop()
		
	def begin(self):
		"""
		Starts the modules and updates the views
		"""
		
		# Grab the camshift class
		self.idm = camshift.Module()
		
		# TODO: Find actual cam device index
		#self.idm.set_capture(1)
		
		#gobject.timeout_add(150, self.update_frame)
		
		# Init and build the GUI
		self.mainGUI = GUI()
		self.mainGUI.buildUI()
		self.mainGUI.main()
		
		# Run the gobject threads
		gobject.threads_init()
		self.loop.run()
	
	def update_frame(self):
		"""
		Updates the UI with the newest capture frame
		"""
		if self.idm is None:
			return True
		
		if(self.mainGUI.cap_image.isVisible):
			self.mainGUI.updateCapture(self.idm.get_image())
		return True
		
	
ctr = Controller()
ctr.begin()