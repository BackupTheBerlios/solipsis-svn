class Address(object):
    """ Represents a Solipsis Address."""

    SEPARATOR = ':'

    def __init__(self, host='', port=0, strAddress=''):
        """ Constructor. Create a new Address object
        host : host name or IP address
        port : port number
        strAddress : a string representing the network address
        """
        self.host = host
        self.port = int(port)

        # override host, port value if strAddress is not null
        if strAddress <> '':
            self.setValueFromString(strAddress)

    def toString(self):
        return str(self.host) + Address.SEPARATOR + str(self.port)

    def getHost(self):
        return self.host

    def getPort(self):
        return self.port

    def setValueFromString(self, strAddress):
        """ Set the new address of this Address object.
        strAddress: a string representing the address '192.235.22.32:8978'
        """
        if strAddress <> '':
            strHost, strPort = strAddress.split(Address.SEPARATOR)
            if strHost <> '':
                self.host = strHost
            if strPort <> '':
                self.port = int(strPort)

    def __eq__(self, other):
        return ( self.getHost() == other.getHost() ) and \
               ( self.getPort() == other.getPort() )

    def __str__(self):
        return self.toString()

