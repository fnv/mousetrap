imgdir = $(datadir)/mouseTrap/images
hicolordir = $(datadir)/icons/hicolor
app_icons = \
	mousetrap-16x16.png	\
	mousetrap-22x22.png	\
	mousetrap-24x24.png	\
	mousetrap-32x32.png	\
	mousetrap-48x48.png	\
	mousetrap-scalable.svg

install-data-local:
	@-$(mkinstalldirs) $(DESTDIR)$(imgdir)
	$(INSTALL_DATA) $(srcdir)/leftClick.png $(DESTDIR)$(imgdir)/leftClick.png
	$(INSTALL_DATA) $(srcdir)/doubleClick.png $(DESTDIR)$(imgdir)/doubleClick.png
	$(INSTALL_DATA) $(srcdir)/leftHold.png $(DESTDIR)$(imgdir)/leftHold.png
	$(INSTALL_DATA) $(srcdir)/middleClick.png $(DESTDIR)$(imgdir)/middleClick.png
	$(INSTALL_DATA) $(srcdir)/rightClick.png $(DESTDIR)$(imgdir)/rightClick.png

	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/16x16/apps
	$(INSTALL_DATA) $(srcdir)/mousetrap-16x16.png $(DESTDIR)$(hicolordir)/16x16/apps/mousetrap.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/22x22/apps
	$(INSTALL_DATA) $(srcdir)/mousetrap-22x22.png $(DESTDIR)$(hicolordir)/22x22/apps/mousetrap.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/24x24/apps
	$(INSTALL_DATA) $(srcdir)/mousetrap-24x24.png $(DESTDIR)$(hicolordir)/24x24/apps/mousetrap.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/32x32/apps
	$(INSTALL_DATA) $(srcdir)/mousetrap-32x32.png $(DESTDIR)$(hicolordir)/32x32/apps/mousetrap.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/48x48/apps
	$(INSTALL_DATA) $(srcdir)/mousetrap-48x48.png $(DESTDIR)$(hicolordir)/48x48/apps/mousetrap.png
	@-$(mkinstalldirs) $(DESTDIR)$(hicolordir)/scalable/apps
	$(INSTALL_DATA) $(srcdir)/mousetrap-scalable.svg $(DESTDIR)$(hicolordir)/scalable/apps/mousetrap.svg

gtk_update_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

install-data-hook:
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating Gtk icon cache."; \
		$(gtk_update_icon_cache); \
	else \
		echo "*** Icon cache not updated.  After install, run this:"; \
		echo "***   $(gtk_update_icon_cache)"; \
	fi

uninstall-hook:
	rm -f $(DESTDIR)$(imgdir)/leftClick.png
	rm -f $(DESTDIR)$(imgdir)/leftHold.png
	rm -f $(DESTDIR)$(imgdir)/middleClick.png
	rm -f $(DESTDIR)$(imgdir)/rightClick.png
	rm -Rf $(DESTDIR)$(datadir)/mouseTrap
