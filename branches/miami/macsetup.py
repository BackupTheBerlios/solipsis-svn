#!/usr/bin/env python
"""
macsetup.py - script for building Solipsis.app

Usage:
    % python macsetup.py py2app

After creating the .app file, it is probably useful to store
it in a compressed archive:
    % zip -9yr Solipsis-macosx10.3.zip Solipsis.app
"""

import os
import sys
import glob
import re

from distutils.core import setup
#import bdist_mpkg

# Local imports
from solipsis import VERSION
from commonsetup import *

application_name = "Solipsis"
version = VERSION
description = "Solipsis, a peer-to-peer system for a massively multi-participant virtual world"
author = "France Telecom R&D"
author_email = "solipsis-tech@lists.berlios.de"
url = "http://solipsis.netofpeers.net/"
license = "COPYRIGHT"

#
# Invoke common setup routines
#
includes = ['solipsis.node.main'] + get_dynamic_modules()
data_files = get_data_files()

#
# Create dynamic setup info
#
template = "dyn/py2app.tmpl.py"
dynfile = template.replace('.tmpl.py', '.py')
print "generating %s" % dynfile

var_replace = {}
var_replace['executable'] = '../MacOS/' + application_name

f = file(template, 'r')
s = f.read()
f.close()
for k, v in var_replace.items():
    s, n = re.subn(r'[^\r\n]+#\s*<%s>([\r\n])' % k, "%s = %s\n\\1" % (k, repr(v)), s)
    if n == 0:
        print "Couldn't find var '%s' in template '%s'. Bailing out." % (k, template)
        sys.exit(1)

f = file(dynfile, 'w')
f.write(s)
f.close()


#
# Launch the distutils machinery with options computed above
#

import py2app

# Note that you must replace hypens '-' with underscores '_'
# when converting option names from the command line to a script.
# For example, the --argv-emulation option is passed as
# argv_emulation in an options dict.
py2app_options = {
    # Map "open document" events to sys.argv.
    # Scripts that expect files as command line arguments
    # can be trivially used as "droplets" using this option.
    # Without this option, sys.argv should not be used at all
    # as it will contain only Mac OS X specific stuff.
    'argv_emulation': True,
    'includes': includes,

    # This is a shortcut that will place MyApplication.icns
    # in the Contents/Resources folder of the application bundle,
    # and make sure the CFBundleIcon plist key is set appropriately.
    #iconfile='MyApplication.icns',
}

setup(
    # Metadata
    name=application_name,
    version=version,
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    license=license,

    # Application data
    app=['navigator.py'],
    data_files=data_files,
    options={
        'py2app': py2app_options,
    }
)
