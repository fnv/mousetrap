

PYTHONPATH=@pyexecdir@

DOC_FILES = \
	mousetrap \
	mousetrap.mousetrap \
	mousetrap.environment \
	mousetrap.debug \
	mousetrap.ui \
	mousetrap.ui.dialogs \
	mousetrap.ui.i18n \
	mousetrap.ui.main \
	mousetrap.ui.settings_gui \
	mousetrap.ui.widgets \
	mousetrap.ui.scripts \
	mousetrap.ui.scripts.screen \
	mousetrap.addons \
	mousetrap.addons.cpu \
	mousetrap.addons.handler \
	mousetrap.addons.recalc \
	mousetrap.lib \
	mousetrap.lib.dbusd \
	mousetrap.lib.httpd \
	mousetrap.lib.mouse \
	mousetrap.lib.settings \
	ocvfw \
	ocvfw.commons \
	ocvfw.debug \
	ocvfw._ocv \
	ocvfw.pocv \
	ocvfw.dev \
	ocvfw.dev.camera \
	ocvfw.idm \
	ocvfw.idm.forehead \
    ocvfw.idm.color



if ENABLE_PYDOC
all:
	for i in $(DOC_FILES); \
	    do pydoc -w $$i; done
endif
