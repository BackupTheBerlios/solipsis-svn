
import sys
import logging
import re

from node import Node
from nodeconnector import NodeConnector
from statemachine import StateMachine
import states


class Bootstrap(object):
    from solipsis.util.geometry import Position
    #dummy_position = Position(2**127 - 2**125 - 3000, 2000000000, 0)
    dummy_position = Position(123456789, 2000000000, 0)

    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params
        self.node = Node(reactor, params)
        self.state_machine = StateMachine(reactor, params, self.node)
        self.node_connector = NodeConnector(reactor, params, self.state_machine)

        self.bootup_entities = self._ParseEntitiesFile(self.params.entities_file)

    def Run(self):
        self.node.position = self.dummy_position
        self.reactor.listenUDP(self.params.port, self.node_connector)
        #self._SimpleFlood()
        self.state_machine.ConnectWithEntities(sender=self.node_connector.SendMessage,
                                                addresses=self.bootup_entities)
        self.reactor.run()

    #
    # Private methods
    #
    def _SimpleHello(self, address):
        import protocol
        message = protocol.Message("HELLO")
        message.args.id_ = "toto"
        message.args.pseudo = "Antoine"
        message.args.position = self.dummy_position
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
        self.reactor.callLater(5.0, self._SimpleFlood)

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
        entities.reverse() # a bit of fun
        return entities

