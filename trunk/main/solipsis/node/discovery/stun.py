
import twisted.internet.defer as defer

import solipsis.node.lib.stun as stun


class _StunDiscovery(stun.StunProtocol):
    def __init__(self, *args, **kargs):
        super(_StunDiscovery, self).__init__(*args, **kargs)

    def Start(self, port, reactor, deferred):
        """
        Start listening for STUN replies.
        """
        self.deferred = deferred
        self.listening = reactor.listenUDP(port, self)
        self.blatServers()

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
    print "STUN discovery..."
    d = defer.Deferred()
    stun = _StunDiscovery(servers=[('127.0.0.1', 3478)])
    # Define timeout callback
    def _timeout():
        stun.Stop()
        d.errback(Exception("STUN timed out"))
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
