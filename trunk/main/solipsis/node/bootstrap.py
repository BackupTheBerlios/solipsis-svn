
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


# Helper (see Python documentation for built-in function __import__)
def _import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class Bootstrap(object):

    def __init__(self, reactor, params):
        """
        Initialize the bootstrap object and all necessary objects.
        Also does the local IP address discovery.
        """
        self.reactor = reactor
        self.params = params
        self.pool = []

        # Local address discovery
        discovery_module = 'local'
        discovery = _import('discovery.' + discovery_module)
        d = discovery.DiscoverAddress(self.reactor, self.params)
        def _succeed(address):
            print "local IP address is %s" % str(address)
            self.local_address = address
            self.reactor.callLater(0, self.LaunchPool)
        def _fail(failure):
            print "Address discovery failed:", str(failure)
            sys.exit(1)
        d.addCallback(_succeed)
        d.addErrback(_fail)

    def Run(self):
        """
        Initiate the network connections and launch the main loop.
        """
        # Enter event loop
        try:
            self.reactor.run()
        except Exception, e:
            print str(e)
            sys.exit(1)

    def LaunchPool(self):
        """
        Launch the pool of local nodes.
        """
        class PoolItem(object):
            def __init__(self, state_machine, node_connector, remote_control):
                self.state_machine = state_machine
                self.node_connector = node_connector
                self.remote_control = remote_control

        if self.params.pool:
            # Prepare a pool of nodes
            entities = []
            for i in range(self.params.pool):
                port = self.params.port + i
                entities.append((self.params.host, port))
                node = Node(self.reactor, self.params)
                node.address = Address(self.local_address, port)
                node.position = Position(random.random() * 2**128, random.random() * 2**128, 0)
                state_machine = StateMachine(self.reactor, self.params, node)
                node_connector = NodeConnector(self.reactor, self.params, state_machine)
                remote_control = RemoteControl(self.reactor, self.params, state_machine)
                self.pool.append(PoolItem(state_machine, node_connector, remote_control))
            if self.params.as_seed:
                self.bootup_entities = entities
            else:
                self.bootup_entities = self._ParseEntitiesFile(self.params.entities_file)
        else:
            # Prepare a single node
            node = Node(self.reactor, self.params)
            node.address = Address(self.local_address, self.params.port)
            node.position = Position(self.params.pos_x, self.params.pos_y, 0)
            state_machine = StateMachine(self.reactor, self.params, node)
            node_connector = NodeConnector(self.reactor, self.params, state_machine)
            remote_control = RemoteControl(self.reactor, self.params, state_machine)
            if self.params.as_seed:
                self.bootup_entities = self._ParseSeedsFile("conf/seed.met")
            else:
                self.bootup_entities = self._ParseEntitiesFile(self.params.entities_file)
            self.pool.append(PoolItem(state_machine, node_connector, remote_control))

        # Launch the network connections
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

