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


from twisted.internet.protocol import DatagramProtocol


class Protocol(DatagramProtocol):
    def __init__(self, receiver):
        self.hosts = []
        self.receiver = receiver

    def SetHosts(self, hosts):
        self.hosts = list(hosts)
    
    def SendMessage(self, text, exclude_addr=None):
        data = text.encode('utf-8')
        for to_host, to_port in self.hosts:
            if exclude_addr is not None and (to_host, to_port) != exclude_addr:
                continue
            self.transport.write(data, (to_host, to_port))

    def datagramReceived(self, data, (from_host, from_port)):
        text = data.decode('utf-8')
        self.receiver(text, (from_host, from_port))


class NetworkLauncher(object):
    def __init__(self, reactor, plugin, port):
        self.reactor = reactor
        self.plugin = plugin
        self.port = port
        self.listening = None
        self.protocol = None

    def Start(self, receiver):
        if self.listening:
            self.Stop()
        self.protocol = Protocol(receiver)
        self.listening = self.reactor.listenUDP(self.port, self.protocol)
        self.SetHosts([])

    def Stop(self):
        self.listening.stopListening()
        self.listening = None
        self.protocol = None

    def SendMessage(self, data):
        assert self.protocol is not None, "Tried to send message but protocol is disabled"
        self.protocol.SendMessage(data)

    def SetHosts(self, hosts):
        # For test purposes, chat with ourselves ;)
        hosts.append((self.listening.getHost().host, self.port))
        self.protocol.SetHosts(hosts)
