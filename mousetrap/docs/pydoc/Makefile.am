
PYTHONPATH=@pyexecdir@

DOC_FILES = \
	mouseTrap \
	mouseTrap.cam \
	mouseTrap.debug \
	mouseTrap.dialogs \
	mouseTrap.info \
	mouseTrap.mainGui \
	mouseTrap.mouse \
	mouseTrap.mouseTrapPreff \
	mouseTrap.mouseTrap \
	mouseTrap.mTCommon \
	mouseTrap.mTDbus \
	mouseTrap.mTServer \
	mouseTrap.preffGui \
	mouseTrap.profiling


if ENABLE_PYDOC
all:
	for i in $(DOC_FILES); \
	    do pydoc -w $$i; done
endif

