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
import sys
import re

def _GnomeSetURLHandler(scheme, cmd_args):
    try:
        import gconf
        client = gconf.client_get_default()
    except:
        return
    basepath = '/desktop/gnome/url-handlers/%s' % scheme
    command = ' '.join([a.replace('%s', '"%s"') for a in cmd_args])
    print "Setting up Gnome URL handler:", command
    client.set_string(basepath + '/command', command)
    client.set_bool(basepath + '/enabled', True)
    client.set_bool(basepath + '/needs_terminal', False)

def _WindowsSetURLHandler(scheme, cmd_args):
    try:
        import _winreg as winreg
    except ImportError:
        return
    slp_k = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r'slp')
    winreg.SetValueEx(slp_k, "", None, winreg.REG_SZ, "URL: Solipsis Protocol")
    winreg.SetValueEx(slp_k, "URL Protocol", None, winreg.REG_SZ, "")
    shell_k = winreg.CreateKey(slp_k, "shell")
    open_k = winreg.CreateKey(shell_k, "open")
    command_k = winreg.CreateKey(open_k, "command")
    command = ' '.join([a.replace('%s', '"%1"') for a in cmd_args])
    print "Setting up Windows URL handler:", command
    winreg.SetValueEx(command_k, "", None, winreg.REG_SZ, command)

def SetURLHandler(scheme, cmd_args):
    _GnomeSetURLHandler(scheme, cmd_args)
    _WindowsSetURLHandler(scheme, cmd_args)

def SetSolipsisURLHandlers(prog_name=None):
    """
    Setup all Solipsis URL handlers. If you are calling this function from
    the navigator itself, you can leave the parameter empty, otherwise you
    *must* give the name/path of the program used to open Solipsis URLs.
    """
    if prog_name is None:
        prog_name = os.path.basename(sys.argv[0])
    prog_path = os.path.abspath(prog_name)
    # In some cases the main program won't be a .py file (e.g. pyexe-generated
    # executable under Windows)
    if os.path.exists(sys.executable) and re.match(r'.*\.py[cow]?$', prog_name, re.IGNORECASE):
        base_args = [sys.executable, prog_path]
    else:
        base_args = [prog_path]
    SetURLHandler('slp', base_args + ['--url', '%s'])
