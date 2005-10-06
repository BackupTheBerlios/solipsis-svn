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
import locale
import shutil

from twisted.internet.error import CannotListenError
from twisted.internet import defer

from solipsis.navigator.main import build_params
from solipsis.navigator.netclient.app import NavigatorApp
from solipsis.navigator.netclient.tests import LOCAL_PORT
from solipsis.services.profile import PROFILE_EXT
from solipsis.services.profile.tests import PROFILE_DIR, FILE_BRUCE, FILE_TEST
from solipsis.services.profile.facade import get_facade

USAGE = "launch.py [pseudo | -B | -T]  [-t] [-p PORT] [-f FILE]"

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
    parser.add_option("-B", "--pseudo-bruce",
                      action="store_true", dest="bruce", default=False,
                      help="bruce profile")
    parser.add_option("-T", "--pseudo-test",
                      action="store_true", dest="test", default=False,
                      help="test profile")
    options, args = parser.parse_args()
    # set pseudo
    if len(args) == 1:
        pseudo =  os.path.join(PROFILE_DIR, args[0])
    else:
        if options.bruce:
            pseudo = FILE_BRUCE
        elif options.test:
            pseudo = FILE_TEST
        else:
            print USAGE
            sys.exit(1)
    sys.argv = []
    # app needs conf env
    os.chdir(root_path)
    params = build_params(options.conf_file)
    params.testing = options.testing
    params.local_port = int(options.port)
    params.node_id = pseudo
    params.pseudo = pseudo
    # launch application
    try:
        print "Pseudo:", pseudo
        navigator = NavigatorApp(params=params)
        def on_error(failure):
            print "***", failure.getErrorMessage()
        def on_connect(result):
            src_path = pseudo + PROFILE_EXT
            dst_path = os.path.join(PROFILE_DIR, get_facade()._desc.node_id + PROFILE_EXT)
            shutil.copyfile(src_path, dst_path)
            get_facade().load()
            print src_path, ">", dst_path
        deferred = defer.Deferred().addCallbacks(on_connect, on_error)
        def on_init(result):
            navigator._TryConnect(deferred)
        navigator.addCallbacks(on_init, on_error)
        navigator.startListening()
    except CannotListenError, err:
        print err

if __name__ == "__main__":
    run()
