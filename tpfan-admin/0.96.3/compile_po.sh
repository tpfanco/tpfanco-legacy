#!/bin/bash

mkdir -p mo
cd po
for pofile in *.po
do
	lang=`echo $pofile | cut -d "." -f 1`
	mkdir -p ../mo/$lang/LC_MESSAGES/
	msgfmt -o ../mo/$lang/LC_MESSAGES/tpfan-admin.mo $pofile
done


