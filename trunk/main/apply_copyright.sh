#!/bin/sh

for i in `find solipsis -name "*.py"`; do
	echo $i
	cat $i | ./apply_copyright.py | cat > $i
done
