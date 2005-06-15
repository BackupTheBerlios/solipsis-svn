#!/usr/bin/env python
"""
setup.py - script for building MyApplication

Usage:
    % python macsetup.py py2app
"""

import os

from distutils.core import setup
import py2app


name = "Solipsis"
version = "0.8.4"
description = "Solipsis, a peer-to-peer system for a massively multi-participant virtual world"
author = "France Telecom R&D"
author_email = "solipsis-tech@lists.berlios.de"
url = "http://solipsis.netofpeers.net"
license = "GNU LGPL"

packages = []
includes = []
resources = []
data_files = []

#
# Find all packages
#
#packages = ['solipsis', 'solipsis.services']
service_dir = 'solipsis/services'
for filename in os.listdir(service_dir):
    path = os.path.join(service_dir, filename)
    if os.path.isdir(path) and not filename.startswith('_'):
        package = path.replace('/', '.')
        packages.append(package)
        includes.append(package + '.plugin')
#print "packages =", packages
print "includes =", includes

#
# Find all resource files and dirs
#
# Please note: base directories of service plugins will be automatically
# included as long as they contain some localization data (.mo files)
resource_dirs = set()
extra_files = [
    'xrc',
    'mo',
    'png', 'gif', 'jpg', 'jpeg',
    'txt', 'html',
    'conf', 'met',
]
for dirpath, dirnames, filenames in os.walk('.'):
    if dirpath.startswith('./dist/') or dirpath.startswith('./build/'):
        continue
    found = False
    files = []
    dirpath = dirpath[2:]
    for filename in filenames:
        # Include files with one of the registered extensions
        for ext in extra_files:
            if filename.endswith('.' + ext):
                break
        else:
            #print "> excluding:", filename
            continue
        path = os.path.join(dirpath, filename)
        resources.append(path)
        files.append(path)
        found = True
    # We must not forget to include directories or everything will end up 
    # in the same place
    if found and dirpath != '.':
        resource_dirs.add(dirpath)
    data_files.append((dirpath, files))
resources = list(resource_dirs) + resources
resources = list(resource_dirs)
#print "resources =", resources
#print "data_files =", data_files

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
#    'packages': packages,
#    'resources': resources,

    # This is a shortcut that will place MyApplication.icns
    # in the Contents/Resources folder of the application bundle,
    # and make sure the CFBundleIcon plist key is set appropriately.
    #iconfile='MyApplication.icns',
}

setup(
    # Metadata
    name=name,
    version=version,
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    license=license,

    # Application data
    app=['navigator.py'],
    #targets=['twistednode.py', 'navigator.py'],
    data_files=data_files,
    options={
        'py2app': py2app_options,
    }
)
