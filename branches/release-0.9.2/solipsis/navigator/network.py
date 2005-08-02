# pylint: disable-msg=C0103,W0142
# Invalid name // Used * or ** magic
#
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
"""Base class for node management. Responsible for connection"""

import threading
import random

from solipsis.navigator.urllistener import URLListenFactory
from solipsis.util.remote import RemoteConnector

class BaseNetworkLoop(threading.Thread):
    """
    NetworkLoop is an event loop running in its own thread.
    It manages socket-based communication with the Solipsis node
    and event-based communication with the User Interface (UI).
    """
    def __init__(self, reactor, ui):
        """
        Builds a network loop from a Twisted reactor and a Wx event handler.
        """
        super(BaseNetworkLoop, self).__init__()
        self.repeat_hello = True
        self.repeat_count = 0
        self.reactor = reactor
        self.ui = ui
        self.remote_connector = RemoteConnector(self.reactor, self.ui)

    def run(self):
        """
        Run the reactor loop.
        """
        self.reactor.run(installSignalHandlers=0)

    #
    # Actions from the UI thread
    #
    def ConnectToNode(self, config_data, *args, **kargs):
        """Establish connection. A deferred may be passed in args and
        will be called when connected"""
        proxy_host = None
        proxy_port = None
        if config_data.connection_type == "local":
            host = "localhost"
            port = config_data.local_control_port
        else:
            host = config_data.host
            port = config_data.port
            if config_data.proxy_mode != "none" and config_data.proxy_host:
                proxy_host = config_data.proxy_host
                proxy_port = config_data.proxy_port
        self.remote_connector.Connect(host, port, proxy_host, proxy_port,
                                      *args, **kargs)

    def DisconnectFromNode(self, *args, **kargs):
        """forward to remote collector. See solipsis.util.remote"""
        self.remote_connector.Disconnect(*args, **kargs)

    def KillNode(self, *args, **kargs):
        """forward to remote collector. See solipsis.util.remote"""
        self.remote_connector.Kill(*args, **kargs)

    def ResetNode(self, *args, **kargs):
        """forward to remote collector. See solipsis.util.remote"""
        self.remote_connector.Reset(*args, **kargs)

    #
    # URL Listener
    #

    def StartURLListener(self, url_port_min, url_port_max=0):
        """listen for incomming commands 'Jump to URL'"""
        if url_port_max:
            url_port = random.randrange(url_port_min, url_port_max + 1)
        else:
            url_port = url_port_min
        try:
            self.reactor.listenTCP(url_port,
                factory=URLListenFactory(self.ui),
                interface="127.0.0.1")
        except Exception, err:
            print "Cannot listen to jump URLs: %s" % str(err)
        else:
            self.ui._UpdateURLPort(url_port)
