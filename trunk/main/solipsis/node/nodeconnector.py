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

import sys

from twisted.internet.protocol import DatagramProtocol

from solipsis.util.utils import set
from solipsis.util.address import Address
from peer import Peer
import protocol


class NodeProtocol(DatagramProtocol):
    def __init__(self, node_connector):
        self.node_connector = node_connector

    def datagramReceived(self, data, address):
        self.node_connector.OnMessageReceived(data, address)

    def SendData(self, data, address):
        self.transport.write(data, address)


class NodeConnector(object):
    no_log = set(['HEARTBEAT'])

    def __init__(self, reactor, params, state_machine, logger):
        self.reactor = reactor
        self.params = params
        self.state_machine = state_machine
        self.logger = logger
        self.parser = protocol.Parser()
        self.node_protocol = NodeProtocol(self)

        self.known_peers = {}
        self.current_peers = {}

    def Start(self, port):
        """
        Start listening to Solipsis messages.
        """
        self.listening = self.reactor.listenUDP(port, self.node_protocol)

    def Stop(self):
        """
        Stop listening.
        """
        self.listening.stopListening()

    def OnMessageReceived(self, data, address):
        """
        Called when a Solipsis message is received.
        """
        host, port = address
        try:
            message = self.parser.ParseMessage(data)
            if message.request not in self.no_log:
                self.logger.debug("<<<< received from %s:%d\n%s" % (host, port, data))
        except Exception, e:
            print str(e)
        else:
            self.state_machine.PeerMessageReceived(message.request, message.args)

    def SendToAddress(self, message, address):
        self._SendMessage(message, address)

    #
    # Internal methods
    #

    def _SendMessage(self, message, address):
        """
        Send a Solipsis message to an address.
        """
        data = self.parser.BuildMessage(message)
        self._SendData(data, address, log=message.request not in self.no_log)

    def _SendData(self, data, address, log=False):
        if isinstance(address, Address):
            host, port = (address.host, address.port)
        else:
            host, port = address
        self.node_protocol.SendData(data, (host, port))
        if log:
            self.logger.debug(">>>> sending to %s:%d\n%s" % (host, port, data))
