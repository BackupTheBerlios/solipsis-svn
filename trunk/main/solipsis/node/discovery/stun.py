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

import twisted.internet.defer as defer

import solipsis.lib.shtoom.stun as stun

stun_section = {
    'servers': ('stun_servers', str, ""),
}
stun_timeout = 2.0

class _StunClient(stun.StunDiscoveryProtocol):
    def __init__(self, reactor, *args, **kargs):
        stun.StunDiscoveryProtocol.__init__(self, *args, **kargs)
        self.reactor = reactor

    def Run(self, port):
        self.d = defer.Deferred()
#         self.timeout = self.reactor.callLater(stun_timeout, self.Timeout)
        self.listening = self.reactor.listenUDP(port, self)
        self.reactor.callLater(0, self.startDiscovery)
        return self.d

    def _Failed(self):
        self.d.errback(Exception("no response"))

    def Timeout(self):
        self._finished = True
        self.listening.stopListening()
        self._Failed()

    def finishedStun(self):
#         self.timeout.cancel()
#         print "You're behind a %r"%(self.natType)
        self.listening.stopListening()
        if self.externalAddress is not None:
            self.d.callback(self.externalAddress)
        else:
            self._Failed()

def DiscoverAddress(port, reactor, params):
    print "Using STUN to get public IP (port: %d)" % port
    d = defer.Deferred()
    params.LoadSection('stun', stun_section)
    servers = params.stun_servers.strip()
    if servers:
        serv_list = [(s.strip(), 3478) for s in servers.split(',')]
        discovery = _StunClient(reactor, servers=serv_list)
    else:
        discovery = _StunClient(reactor)

    # Start listening
    return discovery.Run(port)

