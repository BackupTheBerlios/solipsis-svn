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
import os.path
import sys
import re

from solipsis.util.exception import BadInstall


class Launcher(object):
    """
    This class spawns a local node instance that will connect to other nodes.
    """

    # This is a list of possible file names for the node launcher
    launcher_alternatives = ['twistednode.py', 'twistednode.exe']

    def __init__(self, port=None, control_port=None, custom_args=None):
        self.port = port
        self.control_port = control_port
        if custom_args is not None:
            self.custom_args = list(custom_args)
        else:
            self.custom_args = []
    
    def py2app_args(self):
        # For py2app-bundled applications, we use a stub through the py2app
        # executable (directly launching scripts leads to library missing errors)
        try:
            import dyn.py2app
        except ImportError:
            return None
        else:
            return [dyn.py2app.executable, '--runnode']

    def python_args(self):
        # Find the proper executable in the current dir
        for f in self.launcher_alternatives:
            if os.path.isfile(f):
                prog_name = f
                break
        else:
            return None
        prog_path = os.path.normcase('.' + os.sep + prog_name)
        # We try to keep the same Python interpreter as currently
        if os.path.exists(sys.executable) and re.match(r'.*\.py[cow]?$', prog_name, re.IGNORECASE):
            return [sys.executable, prog_path]
        else:
            return [prog_path]

    def Launch(self):
        # First handle the py2app special case
        methods = [self.py2app_args, self.python_args]
        for m in methods:
            args = m()
            if args:
                break
        else:
            raise BadInstall("No launching method adequate. Could not find any of ('%s') in the main directory"
                % "', '".join(self.launcher_alternatives))
        args +=  ['-q', '-d']
        if self.port:
            args += ['-p', str(self.port)]
        if self.control_port:
            args += ['--control-host', '127.0.0.1']
            args += ['--control-port', str(self.control_port)]
        args += self.custom_args
        cmdline = " ".join(args)
        print "Executing '%s'..." % cmdline

        # Here we use subprocess for portability, but in case it doesn't exist
        # (Python < 2.4) we fall back on os.spawnv - which does not allow direct
        # execution of .py files under Windows.
        try:
            import subprocess
        except ImportError:
            print "(using os.spawnv)"
            return os.spawnv(os.P_NOWAIT, args[0], args) > 0
        else:
            print "(using subprocess.Popen)"
            try:
                subprocess.Popen(cmdline, shell=True)
            except (OSError, ValueError), e:
                print str(e)
                return False
            else:
                return True
