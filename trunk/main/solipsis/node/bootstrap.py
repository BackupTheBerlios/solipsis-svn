
import sys
import logging
import re

from nodeconnector import NodeConnector


class Bootstrap(object):
    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params
        self.node_connector = NodeConnector(reactor, params)
        self.node = self.node_connector.node

        self.bootup_entities = self._ParseEntitiesFile(self.params.entities_file)

    def Run(self):
        self.reactor.listenUDP(self.params.port, self.node_connector)
        self._SimpleFlood()
        self.reactor.run()

    #
    # Private methods
    #
    def _SimpleHello(self, address):
        import protocol
        from solipsis.util.geometry import Position
        message = protocol.Message("HELLO")
        message.args.id_ = "toto"
        message.args.pseudo = "Antoine"
        message.args.position = Position(1000,200,0)
        message.args.calibre = 0
        message.args.orientation = 0
        message.args.address = "127.0.0.1:%d" % self.params.port
        message.args.awareness_radius = 500000
        self.node_connector.SendMessage(message, address)

    def _SimpleBoot(self):
        for address in self.bootup_entities:
            self._SimpleHello(address)

    def _SimpleFlood(self):
        self._SimpleBoot()
        self.reactor.callLater(0, self._SimpleFlood)

    def _ParseEntitiesFile(self, filename):
        f = file(filename)
        entities = []

        for line in f:
            p = line.find('#')
            if p >= 0:
                line = line[:p]
            t = line.strip().split()
            if len(t) >= 2:
                host, port = t[0], int(t[1])
                entities.append((host, port))
        return entities

