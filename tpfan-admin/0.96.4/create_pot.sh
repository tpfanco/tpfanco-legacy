#!/bin/bash

version=`cat src/tpfanadmin/build.py | grep "^version = " | sed  -e "s/version = \"\(.*\)\"/\1/"`

options="--foreign-user --package-name=tpfan-admin --package-version=${version} --msgid-bugs-address=surban84@googlemail.com  --copyright-holder=Sebastian_Urban -d tpfan-admin -o po/tpfan-admin.pot"

xgettext $options src/tpfanadmin/*.py 
xgettext $options -j share/tpfan-admin.glade

