import logging
import twisted.internet.defer as defer

import ntcp.stunt.StuntClient as stunt

stun_section = {
    'servers': ('stun_servers', str, ""),
}

class _NatDiscover(stunt.StuntClient):
    """
    A class for a simpler use of STUNT protocol
    """
    
    log = logging.getLogger("ntcp")
    
    def __init__(self, reactor, *args, **kargs):
        stunt.StuntClient.__init__(self, *args, **kargs)
        self.reactor = reactor

    def Run(self):
        """
        Start the discovery method
        """
        self.d = defer.Deferred()
        #self.reactor.callLater(0, self.startDiscovery)
        self.d = self.startDiscovery()
        return self.d

    def _Failed(self):
        """
        Discovery method failed
        """
        self.d.errback(Exception("no response from servers %s" % self.servers))

    def Timeout(self):
        self._finished = True
        self.listening.stopListening()
        self._Failed()

    def finishedStunt(self):
        """
        The discovery procedure is finished.
        Launches a Defer callback
        """
        print '====================================================\n'
        if not self.d.called:
            self.d.callback(self.natType)
            
    def finishedPortDiscovery(self, address):
        """
        The port discovery procedure for immediate TCP connection
        Launches a callback.

        @param address: the discovered address
        """
        if not self.d.called:
            self.d.callback(address)


def NatDiscovery(reactor, succeed=None):
    """
    Start the discovery procedure for NAT discovery.
    Calls the STUNT implementaion

    @param reactor: The application's twisted.internet.reactor
    @param succed: a function to call if we are in non-bloking mode
    """
    d = defer.Deferred()
    discovery = _NatDiscover(reactor)

    # Start listening
    d = discovery.Run()

    if succeed == None: return d
    else:
        # We are in a non-bloking mode
        succeed(discovery.natType)

def AddressDiscover(reactor, port):
    """
    Start the discovery procedure for global address discovery.
    Calls the STUNT implementaion and discover the global
    address mapping for the given port

    @param reactor: The application's twisted.internet.reactor
    @param port: the local port to bind on
    """
    d = defer.Deferred()
    discovery = _NatDiscover(reactor)

    # Start listening
    return discovery.portDiscovery(port)

