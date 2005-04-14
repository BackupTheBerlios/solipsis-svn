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

## *****************************************************************************
##
##   This module is the main module of SOLIPSIS navigator.
##   It starts the main frame of the application.
##
## *****************************************************************************

# BOGUS: Ensure compatibility with future Python versions
# -> this must be inserted at the top of every module! ;(
from __future__ import division

# Python imports
import sys
import wx
from optparse import OptionParser

# Solipsis imports
from solipsis.navigator.basic.basicFrame import wxMainFrame
from solipsis.util.parameter import Parameters

class BoaApp(wx.App):
    def getParams(self):
        config_file = "conf/solipsis.conf"
        usage = "usage: %prog [-p <port>] [-c <port>] [-n <port>] [firstpeer:port]"
        parser = OptionParser(usage)
#         parser.add_option("-h", "--help", action="help",
#                             help="display help message")
        parser.add_option("-p", "--port", type="int", dest="port",
                            help="port number for all Solipsis connections")
        parser.add_option("-c", "--control_port", type="int", dest="control_port",
                            help="control port for navigator")
        parser.add_option("-n", "--notification_port", type="int", dest="notif_port",
                            help="notification port for navigator")
        return Parameters(parser, config_file=config_file)

    def OnInit(self):
        try:
            params = self.getParams()
        except:
            raise

        wx.InitAllImageHandlers()
        self.main = wxMainFrame(params)
        # needed when running from Boa under Windows 9X
        self.SetTopWindow(self.main)
        self.main.Show();self.main.Hide();self.main.Show()
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()
    sys.exit(0)

if __name__ == '__main__':
    main()
