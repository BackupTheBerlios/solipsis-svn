
import sys
import logging

from twisted.internet.protocol import DatagramProtocol

from node import Node
import protocol


class NodeConnector(DatagramProtocol):
    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params
        self.node = Node(reactor, params, self)
        self.parser = protocol.Parser()

    def datagramReceived(self, data, address):
        host, port = address
        print "received %d bytes from %s:%d" % (len(data), host, port)
        message = self.parser.ParseMessage(data)
        print message.request
        print message.args.__dict__

    def SendMessage(self, message, address):
        """ Send Solipsis message to an address (a (host, port) tuple). """
        data = self.parser.BuildMessage(message)
        self.transport.write(data, address)

