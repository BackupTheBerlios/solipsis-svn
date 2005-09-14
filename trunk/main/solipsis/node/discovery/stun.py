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

_stun_type = None

class _StunClient(stun.StunDiscoveryProtocol):
    stun_answers = {
        stun.NatTypeUDPBlocked:
            "UDP is blocked by your firewall.",
        stun.NatTypeNone:
            "you are directly connected.",
        stun.NatTypeSymUDP:
            "your firewall allows outbound UDP sessions.",
        stun.NatTypeFullCone:
            "you are behind a full-cone NAT.",
        stun.NatTypeSymmetric:
            "you are behind a symmetric NAT.",
        stun.NatTypeRestrictedCone:
            "you are behind an address-restricted full-cone NAT.",
        stun.NatTypePortRestricted:
            "you are behind a port/address-restricted full-cone NAT.",
    }

    def __init__(self, reactor, *args, **kargs):
        stun.StunDiscoveryProtocol.__init__(self, *args, **kargs)
        self.reactor = reactor

    def Run(self, port):
        self.d = defer.Deferred()
#         self.timeout = self.reactor.callLater(stun_timeout, self.Timeout)
        try:
            self.listening = self.reactor.listenUDP(port, self)
        except Exception, e:
            self.d.errback(e)
        self.reactor.callLater(0, self.startDiscovery)
        return self.d

    def _Failed(self):
        self.d.errback(Exception("no response from servers %s" % self.servers))

    def Timeout(self):
        self._finished = True
        self.listening.stopListening()
        self._Failed()

    def finishedStun(self):
        global _stun_type
#         self.timeout.cancel()
        self.listening.stopListening()
        _stun_type = self.natType
        print "STUN answer: %s" % self.stun_answers[_stun_type]
        if self.externalAddress is not None:
            self.d.callback(self.externalAddress)
        else:
            self._Failed()

def NeedsMiddleman():
    if _stun_type in (stun.NatTypeSymUDP, stun.NatTypeRestrictedCone, stun.NatTypePortRestricted):
        return True
    else:
        return False

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

