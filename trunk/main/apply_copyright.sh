#!/bin/sh

for i in `find solipsis -name "*.py"`; do
	echo $i
	tmp=$i.tmp
	./apply_copyright.py < $i > $tmp
	mv -f $tmp $i
done
