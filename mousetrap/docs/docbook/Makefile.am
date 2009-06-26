docsdir = $(datadir)/mouseTrap/docs
docsimgdir = $(datadir)/mouseTrap/docs/figures

XSL=/usr/share/xml/gnome/xslt/docbook/html/db2html.xsl

if ENABLE_DOCBOOK
all:
	xsltproc -o index.html $(XSL) mousetrap.xml
endif

install-data-local:
	@-$(mkinstalldirs) $(DESTDIR)$(docsdir)
	$(INSTALL_DATA) $(srcdir)/*.xml $(DESTDIR)$(docsdir)/
	@-$(mkinstalldirs) $(DESTDIR)$(docsimgdir)
	$(INSTALL_DATA) $(srcdir)/figures/* $(DESTDIR)$(docsimgdir)/
	
