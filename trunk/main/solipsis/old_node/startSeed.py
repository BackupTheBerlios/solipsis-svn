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
#!/usr/local/bin/env python
######################################

## SOLIPSIS Copyright (C) France Telecom

## This file is part of SOLIPSIS.

##    SOLIPSIS is free software; you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as published by
##    the Free Software Foundation; either version 2.1 of the License, or
##    (at your option) any later version.

##    SOLIPSIS is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU Lesser General Public License for more details.

##    You should have received a copy of the GNU Lesser General Public License
##    along with SOLIPSIS; if not, write to the Free Software
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

## ------------------------------------------------------------------------------
## -----                           startup.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the main module of SOLIPSIS.
##   It initializes the node and launches all threads.
##   It involves the bootstrap and the message for network address retrieval
##
## ******************************************************************************

import logging
import sys
import exceptions
from optparse import OptionParser

# Solipsis Packages
from solipsis.util.parameter import Parameters
from solipsis.node.seed import Seed

#################################################################################################
#                                                                                               #
#				     -------  main ---------				        #
#                                                                                               #
#################################################################################################

#-----Step 0: Initialize my informations

def main():
    try:
        config_file = "conf/seed.conf"
        usage = "usage: %prog [-db] [-p <port>] [-x ... -y ...] [-e ...] "
        usage = usage + "[-c <port>] [-n <port>] [-f <file>] [firstpeer:port]"
        parser = OptionParser(usage)
#         parser.add_option("-h", "--help", action="help",
#                             help="display help message")
        parser.add_option("-p", "--port", type="int", dest="port",
                          help="port number for all Solipsis connections")
        parser.add_option("-b", "--robot", action="store_true", dest="bot", default=False,
                          help="bot mode (don't listen for navigator)")
        parser.add_option("-d", "--detach", action="store_true", dest="detach", default=False,
                          help="run in the background")
        parser.add_option("-x", type="long", dest="pos_x",
                          help="X start value")
        parser.add_option("-y", type="long", dest="pos_y",
                          help="Y start value")
        parser.add_option("-e", type="int", dest="expected_neighbours",
                          help="number of expected neighbours")
        parser.add_option("-c", "--control_port", type="int", dest="control_port",
                          help="control port for navigator")
        parser.add_option("-n", "--notification_port", type="int", dest="notif_port",
                          help="notification port for navigator")
        parser.add_option("-f", "--file", dest="config_file", default=config_file,
                          help="configuration file")
        parser.add_option("-M", "--memdebug", action="store_true", dest="memdebug", default=False,
                          help="display periodic memory occupation statistics")
        (options, args) = parser.parse_args()
        port = str(options.port)
        defaults = {}
        defaults['logid'] = port
        params = Parameters(parser, defaults=defaults)

        if (params.detach):
            # Create background process for daemon-like operation
            import os, sys, signal
            # Ignore SIGHUP so as not to kill the child when the parent leaves
            signal.signal(signal.SIGHUP, signal.SIG_IGN)

            # Fork and kill the parent process
            if (os.fork()):
                os._exit(0)

            # The child detaches itself from the console
            os.setsid()
            os.chdir("/")
            os.umask(0)

            # Fork and kill the parent proces
            if (os.fork()):
                os._exit(0)

        # Create node and enter main loop
        try:
            # See Psyco documentation: http://psyco.sourceforge.net/psycoguide/module-psyco.html
#             import psyco
#             psyco.profile(watermark=0.01, halflife=10, time=600)
            myNode = Seed(params)
            myNode.mainLoop()
        except Exception, e:
            print "Aborting\n" + str(e)
            raise
            import sys
            sys.exit(1)
    except:
        raise

if __name__ == '__main__':
    main()

