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

import threading

from solipsis.util.uiproxy import UIProxy
from solipsis.util.remote import RemoteConnector

from twisted.internet import protocol, reactor, defer
from twisted.protocols import basic

class NetworkLoop(threading.Thread):
    """
    NetworkLoop is an event loop running in its own thread.
    It manages socket-based communication with the Solipsis node
    and event-based communication with the User Interface (UI).
    """
    def __init__(self, reactor, ui_service):
        """
        Builds a network loop from a Twisted reactor and a Wx event handler.
        """
        super(NetworkLoop, self).__init__()
        self.repeat_hello = True
        self.repeat_count = 0
        self.ui = UIProxy(ui_service)
        self.reactor = reactor

        self.angle = 0.0
        self.remote_connector = RemoteConnector(self.reactor, self.ui)

    def run(self):
        """
        Run the reactor loop.
        """
        self.reactor.run(installSignalHandlers=0)

    #
    # Actions from the UI thread
    #
    def ConnectToNode(self, *args, **kargs):
        self.remote_connector.Connect(*args, **kargs)

    def DisconnectFromNode(self, *args, **kargs):
        self.remote_connector.Disconnect(*args, **kargs)

    def KillNode(self, *args, **kargs):
        self.remote_connector.Kill(*args, **kargs)

class SolipsisUiProtocol(basic.LineReceiver):

    def __init__(self):
        self.cmd = None
        
    def lineReceived(self, line):
        if not self.cmd:
            try:
                cmd = "do_" + line.strip().lower()
                self.cmd = getattr(self.factory, cmd)
            except AttributeError:
                self.transport.write("%s not a valid command\n"% line)
                self.transport.loseConnection()
        else:
            self.cmd(line)
            self.transport.loseConnection()

class SolipsisUiFactory(protocol.ServerFactory):

    protocol = SolipsisUiProtocol

    def __init__(self, application):
        self.app = application

    # UI events
    def do_check(self, arg):
        print "calling _CheckNodeProxy" 
        self.app._CheckNodeProxy()

    # UI events in menu
    def do_about(self, arg):
        print "calling _About" 
        self.app._About(arg)

    def do_create(self, arg):
        print "calling _CreateNode" 
        self.app._CreateNode(arg)

    def do_connect(self, arg):
        print "calling _OpenConnect" 
        self.app._OpenConnect(arg)
        
    def do_disconnect(self, arg):
        print "calling _Disconnect" 
        self.app._Disconnect(arg)

    def do_kill(self, arg):
        print "calling _Kill" 
        self.app._Kill(arg)

    def do_jump(self, arg):
        print "calling _JumpNear" 
        self.app._JumpNear(arg)

    def do_pref(self, arg):
        print "calling _Preferences" 
        self.app._Preferences(arg)

    def do_quit(self, arg):
        print "calling _Quit" 
        self.app._Quit(arg)

    def do_display(self, arg):
        print "calling _DisplayNodeAddress" 
        self.app._DisplayNodeAddress(arg)

    # UI events in viewport
    def do_go(self, arg):
        print "calling _LeftClickViewport" 
        self.app._LeftClickViewportarg()

    def do_menu(self, arg):
        print "calling _RightClickViewport" 
        self.app._RightClickViewport(arg)

    def do_hover(self, arg):
        print "calling _HoverViewport" 
        self.app._HoverViewport(arg)

    def do_key(self, arg):
        print "calling _KeyPressViewport" 
        self.app._KeyPressViewport(arg)
        
