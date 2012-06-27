#!/bin/bash

version=`cat src/tpfanadmin/build.py | grep "^version = " | sed  -e "s/version = \"\(.*\)\"/\1/"`
bzr export ../packages/tarballs/tpfan-admin-${version}.tar.gz
cd ../packages/tarballs
ln -sf tpfan-admin-${version}.tar.gz tpfan-admin_${version}.orig.tar.gz

