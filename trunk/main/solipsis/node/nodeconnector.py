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
import logging
try:
    set
except:
    from sets import Set as set

from twisted.internet.protocol import DatagramProtocol

import protocol


class NodeConnector(DatagramProtocol):
    no_log = set(['HEARTBEAT'])

    def __init__(self, reactor, params, state_machine):
        self.reactor = reactor
        self.params = params
        self.state_machine = state_machine
        self.parser = protocol.Parser()

    def datagramReceived(self, data, address):
        """
        Called when a Solipsis message is received.
        """
        host, port = address
        try:
            message = self.parser.ParseMessage(data)
            if message.request not in self.no_log:
                logging.debug("<<<< received from %s:%d\n%s" % (host, port, data))
        except Exception, e:
            print str(e)
        else:
            self.state_machine.PeerMessageReceived(message.request, message.args)

    def Start(self, port):
        """
        Start listening to Solipsis messages.
        """
        self.listening = self.reactor.listenUDP(port, self)

    def Stop(self):
        """
        Stop listening.
        """
        self.listening.stopListening()

    def SendMessage(self, message, address):
        """
        Send a Solipsis message to an address.
        """
        # This nonsense should really be wiped out...
        from solipsis.util.address import Address
        if isinstance(address, Address):
            host, port = (address.host, address.port)
        else:
            host, port = address
        if not host:
            host = "127.0.0.1"

        data = self.parser.BuildMessage(message)
        if message.request not in self.no_log:
            logging.debug(">>>> sending to %s:%d\n%s" % (host, port, data))
        self.transport.write(data, (host, port))

