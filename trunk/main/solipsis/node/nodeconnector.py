
import sys
import logging

from twisted.internet.protocol import DatagramProtocol

import protocol


class NodeConnector(DatagramProtocol):
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
            logging.debug("received from <<<< %s:%d\n%s" % (host, port, data))
        except Exception, e:
            print str(e)
        else:
            self.state_machine.PeerMessageReceived(message.request, message.args)

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
        logging.debug("sending to >>>> %s:%d\n%s" % (host, port, data))
        self.transport.write(data, (host, port))

