
import sys
import logging
import re

from solipsis.util.geometry import Position
from node import Node
from nodeconnector import NodeConnector
from statemachine import StateMachine
import states


class Bootstrap(object):
#     dummy_position = Position(2**127 - 2**125 - 30000000000, 2000000000, 0)
    dummy_position = Position(2**127 - 2**125 - 30000000000, 2**127 - 2**125 - 30000000000, 0)
#     dummy_position = Position(123456789, 2000000000, 0)

    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params
        self.node = Node(reactor, params)
        self.state_machine = StateMachine(reactor, params, self.node)
        self.node_connector = NodeConnector(reactor, params, self.state_machine)
        self.node.position = Position(self.params.pos_x, self.params.pos_y, 0)

        if self.params.as_seed:
            self.bootup_entities = self._ParseSeedsFile("conf/seed.met")
        else:
            self.bootup_entities = self._ParseEntitiesFile(self.params.entities_file)
            self.node.position = self.dummy_position

    def Run(self):
        # Open Solipsis main port
        try:
            self.reactor.listenUDP(self.params.port, self.node_connector)
        except Exception, e:
            print str(e)
            sys.exit(1)

        # Setup the initial state
        message_sender = self.node_connector.SendMessage
        self.state_machine.Init(message_sender, self.bootup_entities)
        if self.params.as_seed:
            self.state_machine.ImmediatelyConnect()
        else:
            self.state_machine.TryConnect()

        # Enter event loop
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

    def _ParseSeedsFile(self, filename):
        f = file(filename)
        seeds = []

        for line in f:
            p = line.find('#')
            if p >= 0:
                line = line[:p]
            t = line.strip().split()
            if len(t) >= 1:
                host, port = "127.0.0.1", int(t[0])
                if port != self.params.port:
                    seeds.append((host, port))
        return seeds

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

