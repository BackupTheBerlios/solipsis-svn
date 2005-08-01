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
import logging
import exceptions
from optparse import OptionParser

from twisted.internet import reactor

# Solipsis Packages
from solipsis.util.parameter import Parameters
from bootstrap import Bootstrap


def run_loop(params):
    bootstrap = Bootstrap(reactor, params)
    bootstrap.Run()


def main():
    config_file = "conf/solipsis.conf"
    usage = "usage: %prog [-dbqPM] [-p <port>] [--pool <nodes>] (-c <controller>)*"
    parser = OptionParser(usage)
    # Basic options
    parser.add_option("-p", "--port", type="int", dest="port",
                        help="port number for all Solipsis connections")
    parser.add_option("-b", "--robot", action="store_true", dest="bot", default=False,
                        help="bot mode (no default controller)")
    parser.add_option("-d", "--daemon", action="store_true", dest="daemon", default=False,
                        help="run in the background")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False,
                        help="run quietly")

    # Advanced options
    parser.add_option("-c", "--controller", action="append", dest="controllers", default=[],
                        help="specify a controller (multiple occurences allowed)")
    parser.add_option("-f", "--conf", dest="config_file", default=config_file,
                        help="configuration file")
    parser.add_option("", "--pool", type="int", dest="pool", default=0,
                        help="pool of nodes")
    parser.add_option("", "--seed", action="store_true", dest="as_seed", default=False,
                        help="launch node as seed")

    # TODO: make controller-specific options specifiable by the given controller
    parser.add_option("", "--control-host", dest="xmlrpc_host", default="",
                        help="control host")
    parser.add_option("", "--control-port", type="int", dest="xmlrpc_port", default=0,
                        help="control port")

    # Debug/developper options
    parser.add_option("-P", "--profile", action="store_true", dest="profile", default=False,
                        help="profile execution to node.prof")
    parser.add_option("-e", type="int", dest="expected_neighbours",
                        help="number of expected neighbours")
    parser.add_option("-x", type="long", dest="pos_x",
                        help="X start value")
    parser.add_option("-y", type="long", dest="pos_y",
                        help="Y start value")

    # (Ignored) stub option inherited from navigator
    parser.add_option("", "--runnode", action="store_true", help="(internal use)")

    params = Parameters(parser, config_file=config_file)

    if (params.daemon):
        # Create background process for daemon-like operation
        try:
            os.fork, os.setsid, os.umask
        except AttributeError:
            print "cannot launch into background, ignoring"
        else:
            # Ignore SIGHUP so as not to kill the child when the parent leaves
            import signal
            signal.signal(signal.SIGHUP, signal.SIG_IGN)

            # Fork and kill the parent process
            if (os.fork()):
                os._exit(0)

            # The child detaches itself from the console
            os.setsid()
            #os.chdir("/")
            os.umask(0)

            # Fork and kill the parent proces
            if (os.fork()):
                os._exit(0)

    # Create node and enter main loop
    try:        
        global profile_run
        profile_run = lambda: run_loop(params)
        if (params.profile):
            # See profiler documentation:
            import hotshot
            profile = hotshot.Profile("node.prof")
            profile.run(__name__ + ".profile_run()")
            profile.close()
            #import profile
            #profile.run(__name__ + ".profile_run()", "node.prof")
        else:
            # See Psyco documentation: http://psyco.sourceforge.net/psycoguide/module-psyco.html
            #~ try:
                #~ import psyco
                #~ psyco.profile(time=240)
            #~ except ImportError:
                #~ print "You can speed up this program by installing psyco (http://psyco.sourceforge.net/)."
            profile_run()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()

