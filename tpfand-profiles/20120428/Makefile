DESTDIR=/

all:

clean:

install: all	
	install -d $(DESTDIR)/usr/share/tpfand/models
	install -d $(DESTDIR)/usr/share/tpfand/models/by-id
	install -m 644 models/by-id/* $(DESTDIR)/usr/share/tpfand/models/by-id
	install -d $(DESTDIR)/usr/share/tpfand/models/by-name	
	echo Installation complete.	

uninstall:
	rm -rf $(DESTDIR)/usr/share/tpfand/models



