
import sys
import logging
import random

from solipsis.util.geometry import Position
from solipsis.util.address import Address
from node import Node
from nodeconnector import NodeConnector
from control import RemoteControl
from statemachine import StateMachine

import controller.xmlrpc


class Bootstrap(object):
#     dummy_position = Position(2**127 - 2**125 - 30000000000, 2000000000, 0)
    dummy_position = Position(2**127 - 2**125 - 30000000000, 2**127 - 2**125 - 30000000000, 0)
#     dummy_position = Position(123456789, 2000000000, 0)

    def __init__(self, reactor, params):
        class PoolItem(object):
            def __init__(self, state_machine, node_connector, remote_control):
                self.state_machine = state_machine
                self.node_connector = node_connector
                self.remote_control = remote_control

        self.reactor = reactor
        self.params = params
        self.pool = []

        if self.params.pool:
            # Prepare a pool of nodes
            entities = []
            for i in range(self.params.pool):
                port = self.params.port + i
                entities.append((self.params.host, port))
                node = Node(reactor, params)
                node.address = Address(self.params.host, port)
                node.position = Position(random.random() * 2**128, random.random() * 2**128, 0)
                state_machine = StateMachine(reactor, params, node)
                node_connector = NodeConnector(reactor, params, state_machine)
                remote_control = RemoteControl(reactor, params, state_machine)
                self.pool.append(PoolItem(state_machine, node_connector, remote_control))
            if self.params.as_seed:
                self.bootup_entities = entities
            else:
                self.bootup_entities = self._ParseEntitiesFile(self.params.entities_file)
        else:
            # Prepare a single node
            node = Node(reactor, params)
            node.position = Position(self.params.pos_x, self.params.pos_y, 0)
            state_machine = StateMachine(reactor, params, node)
            node_connector = NodeConnector(reactor, params, state_machine)
            remote_control = RemoteControl(self.reactor, self.params, state_machine)
            if self.params.as_seed:
                self.bootup_entities = self._ParseSeedsFile("conf/seed.met")
            else:
                self.bootup_entities = self._ParseEntitiesFile(self.params.entities_file)
                node.position = self.dummy_position
            self.pool.append(PoolItem(state_machine, node_connector, remote_control))


    def Run(self):
        for i, p in enumerate(self.pool):
            # Open Solipsis main port
            sender = p.node_connector.SendMessage
            p.state_machine.Init(sender, p.remote_control, self.bootup_entities)
            try:
                p.node_connector.Start(i)
            except Exception, e:
                print str(e)
                sys.exit(1)
            self.reactor.addSystemEventTrigger('during', 'shutdown', p.node_connector.Stop)

            # Setup the initial state
            if self.params.as_seed:
                p.state_machine.ImmediatelyConnect()
            else:
                p.state_machine.TryConnect()
            self.reactor.addSystemEventTrigger('before', 'shutdown', p.state_machine.Close)
            self.reactor.addSystemEventTrigger('after', 'shutdown', p.state_machine.DumpStats)

            # Start remote controller
            if not self.params.bot:
                x = controller.xmlrpc.Controller(self.reactor, self.params, p.remote_control)
                x.Start(i)
                self.reactor.addSystemEventTrigger('before', 'shutdown', x.Stop)

        # Enter event loop
        try:
            self.reactor.run()
        except Exception, e:
            print str(e)


    #
    # Private methods
    #
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

