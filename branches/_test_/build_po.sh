#!/bin/sh

function do_po() {
	PO_DOMAIN=$1
	PO_DIR=./po
	PO_TEMPLATE=$PO_DIR/messages.pot
	MSG_DIRS=$PO_DIR/*/LC_MESSAGES

	# 1. Build message template from source code and resource files

	echo "extracting strings"

	GETTEXT_OPTIONS="-L python -o $PO_TEMPLATE --from-code utf-8 --force-po"
	GETTEXT_FIRST="xgettext $GETTEXT_OPTIONS"
	GETTEXT="xgettext -j $GETTEXT_OPTIONS"

	#FIND_OPTIONS='-not -path "*/services/*/*"'
	XRC_FILES=`find -name '*.xrc' -not -path "*/services/*/*"`
	PY_FILES=`find -name '*.py' -not -path "*/services/*/*"`

	echo "" | $GETTEXT_FIRST -
	if [ "$XRC_FILES" != "" ] ; then
		wxrc -g $XRC_FILES | $GETTEXT --no-location -
	fi
	$GETTEXT $PY_FILES

	# 2. Create or update PO files

	for msgdir in $MSG_DIRS ; do
		po=$msgdir/$PO_DOMAIN.po
		echo "updating $po"
		touch $po
		msgmerge -s -U $po $PO_TEMPLATE
	done

	# 3. Compile PO files

	for msgdir in $MSG_DIRS ; do
		po=$msgdir/$PO_DOMAIN.po
		mo=`echo "$po" | sed 's/\.po$/.mo/'`
		echo "compiling $mo"
		msgfmt -o $mo $po
	done
}

echo "** Main program **"
MAIN_DIR=`pwd`
do_po solipsis

PLUGIN_DIR=solipsis/services
PLUGINS=`find $PLUGIN_DIR -type d -regex "$PLUGIN_DIR/[^./]*" -printf "%f "`
for plugin in $PLUGINS ; do
	echo "** Plugin '$plugin' **"
	cd $MAIN_DIR
	cd $PLUGIN_DIR/$plugin
	mkdir -p po/fr/LC_MESSAGES
	do_po solipsis_$plugin
done
cd $MAIN_DIR
