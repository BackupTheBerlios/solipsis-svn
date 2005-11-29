class NTCPAddress(object):
    """
    Object representing an NTCP socket endpoint.

    @ivar type: A string describing the type of transport, either 'TCP' or 'UDP'.
    @ivar host: A string containing the dotted-quad IP address.
    @ivar port: An integer representing the port number.
    """

    
    def __init__(self, type, host, port):
        self.type = type
        self.host = host
        self.port = port


class IConnector:
    """Object used to interface between connections and protocols.
    Wrap the real connector until his creation.

    Each IConnector manages one connection.
    """

    def stopConnecting(self):
        """Stop attempting to connect."""
        pass

    def disconnect(self):
        """Disconnect regardless of the connection state.

        If we are connected, disconnect, if we are trying to connect,
        stop trying.
        """
        pass

    def connect(self):
        """Try to connect to remote address."""
        pass

    def getDestination(self):
        """Return destination this will try to connect to.

        This will not be an IAddress implementing object.
        """
        return NTCPAddress('NTCP', self.host, self.port)


