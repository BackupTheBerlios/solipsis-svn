
import twisted.internet.defer as defer

import solipsis.node.lib.stun as stun

stun_section = {
    'servers': ('stun_servers', str, ""),
}

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
    stun = _StunDiscovery(servers=serv_list)
    # Define timeout callback
    def _timeout():
        stun.Stop()
        d.errback(Exception("timed out with servers %s" % servers))
    timeout = reactor.callLater(3.0, _timeout)
    # Define intermediary succeed callback
    def _succeed(value):
        stun.Stop()
        timeout.cancel()
        return value
    d.addCallback(_succeed)
    # Start listening
    stun.Start(port, reactor, d)
    return d
