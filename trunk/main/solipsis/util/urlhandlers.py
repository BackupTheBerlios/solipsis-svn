# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>

import os

def _GnomeSetURLHandler(scheme, progname, *args):
    try:
        import gconf
        client = gconf.client_get_default()
    except:
        return
    basepath = '/desktop/gnome/url-handlers/%s' % scheme
    command = progname + ' ' + ' '.join([a.replace('%s', '%s') for a in args])
    print "Setting up Gnome URL handler:", command
    client.set_string(basepath + '/command', command)
    client.set_bool(basepath + '/enabled', True)
    client.set_bool(basepath + '/needs_terminal', False)

def _WindowsSetURLHandler(scheme, progname, *args):
    pass

def SetURLHandler(scheme, progname, *args):
    _GnomeSetURLHandler(scheme, progname, *args)
    _WindowsSetURLHandler(scheme, progname, *args)
