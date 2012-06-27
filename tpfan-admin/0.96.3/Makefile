DESTDIR=/

all: man pofiles

pofiles:
	./compile_po.sh

man: tpfan-admin.1

tpfan-admin.1: man/tpfan-admin.pod
	pod2man --section=1 --release=Version\ `cat src/tpfanadmin/build.py | grep "^version = " | sed  -e "s/version = \"\(.*\)\"/\1/"` --center "" man/tpfan-admin.pod > tpfan-admin.1

clean:
	rm -f tpfan-admin.1
	rm -f src/tpfanadmin/*.pyc
	rm -rf mo

install: all
	install -d ${DESTDIR}/usr/share/pyshared/tpfanadmin
	install -m 644 src/tpfanadmin/* ${DESTDIR}/usr/share/pyshared/tpfanadmin
	install -d ${DESTDIR}/usr/share/tpfan-admin/
	install -m 644 share/* ${DESTDIR}/usr/share/tpfan-admin/
	install -d ${DESTDIR}/usr/bin
	install -m 755 wrappers/tpfan-admin ${DESTDIR}/usr/bin/
	install -d ${DESTDIR}/usr/share/tpfan-admin/locales/
	cp -av mo/* ${DESTDIR}/usr/share/tpfan-admin/locales/
	install -d ${DESTDIR}/usr/share/applications
	install -m 644 share/tpfan-admin.desktop ${DESTDIR}/usr/share/applications

uninstall:
	rm -rf ${DESTDIR}/usr/share/pyshared/tpfanadmin
	rm -rf ${DESTDIR}/usr/share/tpfan-admin/
	rm -f ${DESTDIR}/usr/bin/tpfan-admin
	rm -f ${DESTDIR}/usr/share/applications/tpfan-admin.desktop


