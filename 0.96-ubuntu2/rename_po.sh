#!/bin/bash

for file in po/tpfan-admin-*.po ;
do
	newfile=`echo $file | sed -e 's/tpfan-admin-//'`
	echo "$file -> $newfile"
	mv -f $file $newfile
done

