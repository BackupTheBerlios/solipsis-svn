#!/bin/sh

PO_DOMAIN=solipsis
PO_DIR=./po
PO_TEMPLATE=$PO_DIR/messages.pot
PO_FILES=$PO_DIR/*/LC_MESSAGES/$PO_DOMAIN.po


# 1. Build message template from source code and resource files

echo "extracting strings"

GETTEXT_OPTIONS="-L python -o $PO_TEMPLATE --from-code utf-8 --force-po"
GETTEXT_FIRST="xgettext $GETTEXT_OPTIONS"
GETTEXT="xgettext -j $GETTEXT_OPTIONS"

echo "" | $GETTEXT_FIRST -
wxrc -g `find -name "*.xrc"` | $GETTEXT -
$GETTEXT `find -name "*.py"`

# 2. Update already existing PO files

for po in $PO_FILES ; do
	echo "updating $po"
	msgmerge -s -U $po $PO_TEMPLATE
done

# 3. Compile PO files

for po in $PO_FILES ; do
	mo=`echo "$po" | sed 's/\.po$/.mo/'`
	echo "compiling $mo"
	msgfmt -o $mo $po
done
