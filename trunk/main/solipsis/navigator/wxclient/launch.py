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

from solipsis.util.exception import BadInstall


class Launcher(object):
    """
    This class spawns a local node instance that will connect to other nodes.
    """

    # This is a list of possible file names for the node launcher
    launcher_alternatives = ['twistednode.py', 'twistednode.exe']

    def __init__(self, port, custom_args=None):
        self.port = port
        if custom_args is not None:
            self.custom_args = list(custom_args)
        else:
            self.custom_args = []
        # Find the proper executable in the current dir
        for f in self.launcher_alternatives:
            if os.path.isfile(f):
                self.launcher_name = f
                break
        else:
            raise BadInstall("could not find any of ('%s') in the main directory"
                % "', '".join(self.launcher_alternatives))
    
    def Launch(self):
        prog_name = os.path.normcase('.' + os.sep + self.launcher_name)
        args = [prog_name]
        args +=  ['-q', '-d', '-p', str(self.port)]
        #~ args +=  ['-d', '-p', str(self.port)]
        args += self.custom_args
        cmdline = " ".join(args)
        print "Executing '%s'..." % cmdline

        # Here we use subprocess for portability, but in case it doesn't exist
        # (Python < 2.4) we fall back on os.spawnv which does not allow direct
        # execution of .py files under Windows.
        try:
            import subprocess
        except ImportError:
            print "(using os.spawnv)"
            return os.spawnv(os.P_NOWAIT, prog_name, args) > 0
        else:
            print "(using subprocess.Popen)"
            try:
                subprocess.Popen(cmdline, shell=True)
            except (OSError, ValueError), e:
                print str(e)
                return False
            else:
                return True
