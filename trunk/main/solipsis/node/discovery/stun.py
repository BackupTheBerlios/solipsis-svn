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

import solipsis.node.lib.stun as stun

stun_section = {
    'servers': ('stun_servers', str, ""),
}
stun_timeout = 2.0


class _StunDiscovery(stun.StunProtocol):
    def __init__(self, *args, **kargs):
        super(_StunDiscovery, self).__init__(*args, **kargs)

    def Start(self, port, reactor, deferred):
        """
        Start listening for STUN replies.
        """
        self.deferred = deferred
        self.listening = reactor.listenUDP(port, self)
        for host, port in self.servers:
            def _resolved(host, port):
                self.sendRequest((host, port))
            def _unresolved(failure):
                print failure.getErrorMessage()
            d = reactor.resolve(host)
            d.addCallback(_resolved, port)
            d.addErrback(_unresolved)

    def Stop(self):
        """
        Stop listening.
        """
        self.listening.stopListening()

    def gotMappedAddress(self, addr, port):
        """
        Called back when STUN discovered our public address.
        """
        if not self.deferred.called:
            self.deferred.callback((addr, int(port)))

def DiscoverAddress(port, reactor, params):
    d = defer.Deferred()
    params.LoadSection('stun', stun_section)
    servers = params.stun_servers or '127.0.0.1'
    serv_list = [(s.strip(), 3478) for s in servers.split(',')]
    discovery = _StunDiscovery(servers=serv_list)
    # Define timeout callback
    def _timeout():
        discovery.Stop()
        d.errback(Exception("timed out with servers %s" % servers))
    timeout = reactor.callLater(stun_timeout, _timeout)
    # Define intermediary succeed callback
    def _succeed(value):
        discovery.Stop()
        timeout.cancel()
        return value
    d.addCallback(_succeed)
    # Start listening
    discovery.Start(port, reactor, d)
    return d
