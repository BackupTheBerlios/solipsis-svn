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
import random

from solipsis.util.uiproxy import UIProxy
from solipsis.util.remote import RemoteConnector

from urllistener import URLListenFactory


class NetworkLoop(threading.Thread):
    """
    NetworkLoop is an event loop running in its own thread.
    It manages socket-based communication with the Solipsis node
    and event-based communication with the User Interface (UI).
    """
    def __init__(self, reactor, ui):
        """
        Builds a network loop from a Twisted reactor and a Wx event handler.
        """
        super(NetworkLoop, self).__init__()
        self.ui = UIProxy(ui)
        self.reactor = reactor

        self.angle = 0.0
        self.remote_connector = RemoteConnector(self.reactor, self.ui)

    def StartURLListener(self, url_port_min, url_port_max=0):
        if url_port_max:
            url_port = random.randrange(url_port_min, url_port_max + 1)
        else:
            url_port = url_port_min
        try:
            self.reactor.listenTCP(url_port,
                factory=URLListenFactory(self.ui),
                interface="127.0.0.1")
        except Exception, e:
            print "Cannot listen to jump URLs: %s" % str(e)
        else:
            self.ui._UpdateURLPort(url_port)

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
