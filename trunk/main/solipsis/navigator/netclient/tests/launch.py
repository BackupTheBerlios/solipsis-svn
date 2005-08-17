#!/usr/bin/env python

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

import os, sys
import socket
import os.path
import solipsis
import optparse

from twisted.internet.error import CannotListenError
from solipsis.navigator.main import build_params
from solipsis.navigator.netclient.app import NavigatorApp
from solipsis.navigator.netclient.tests import LOCAL_PORT

USAGE = "launch.py [-t] [-p PORT] [-f FILE] [-d]"

def run():
    # get conf file
    solipsis_path = os.path.abspath(os.path.dirname(solipsis.__file__))
    root_path = os.path.normpath(os.sep.join([solipsis_path, ".."]))
    conf_file = os.sep.join([root_path, "conf", "solipsis.conf"])
    # get options
    parser = optparse.OptionParser(USAGE)
    parser.add_option("-t", "--testing",
                      action="store_true", dest="testing", default=False,
                      help="execute within trial testing framework")
    parser.add_option("-p", "--port",
                      action="store", dest="port", default=LOCAL_PORT,
                      help="port which navigator listens to")
    parser.add_option("-f", "--config-file",
                      action="store", dest="conf_file", default=conf_file,
                      help="file to read configuration from")
    parser.add_option("-d", "--dual",
                      action="store_true", dest="dual", default=False,
                      help="launch two processes on port 23500 & 23501")
    options, args = parser.parse_args()
    sys.argv = []
    if options.dual:
        # launch two applications
        print "./launch.py"
        os.spawnv(os.P_NOWAIT, "./launch.py", ["launch.py"])
        print "./launch.py -p 23501"
        os.spawnv(os.P_NOWAIT, "./launch.py", ["launch.py", "-p",  "23501"])
    else:
        # app needs conf env
        os.chdir(root_path)
        params = build_params(options.conf_file)
        params.testing = options.testing
        params.local_port = int(options.port)
        # launch application
        try:
            navigator = NavigatorApp(params=params)
        except CannotListenError, err:
            print err

if __name__ == "__main__":
    run()
