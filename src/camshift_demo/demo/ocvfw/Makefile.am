ocvfw_pathdir=$(pyexecdir)

ocvfw_python_PYTHON = \
	debug.py \
	pocv.py \
	commons.py \
	__init__.py \
	_ocv.py


SUBDIRS = dev haars idm

ocvfw_pythondir=$(pyexecdir)/ocvfw

install-exec-hook:
	chmod a+rx $(ocvfw_pythondir) -R
