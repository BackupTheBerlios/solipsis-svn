
import sys
import logging
import random

import twisted.internet.defer as defer

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


class NodeLauncher(object):
    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params

    def Prepare(self, pool_num=0):
        """
        Prepare the node and return the assigned (host, port) tuple.
        """
        self.host = self.params.host or "127.0.0.1"
        self.port = self.params.port + pool_num
        self.control_port = self.params.control_port + pool_num
        node = Node(self.reactor, self.params)
        if self.params.pool:
            node.position = Position(random.random() * 2**128, random.random() * 2**128, 0)
        else:
            node.position = Position(self.params.pos_x, self.params.pos_y, 0)
        self.state_machine = StateMachine(self.reactor, self.params, node)
        self.node_connector = NodeConnector(self.reactor, self.params, self.state_machine)
        self.remote_control = RemoteControl(self.reactor, self.params, self.state_machine)

        # Local address discovery
        discovery_module = 'local'
#         discovery_module = 'stun'
        discovery = _import('discovery.' + discovery_module)
        d = discovery.DiscoverAddress(self.port, self.reactor, self.params)
        def _succeed(address):
            self.host, self.port = address
            node.address = Address(self.host, self.port)
            return self.host, self.port
        def _fail(failure):
            print "Address discovery failed:", str(failure)
            sys.exit(1)
        d.addCallback(_succeed)
        d.addErrback(_fail)
        return d

    def Launch(self, bootup_entities):
        """
        Launch the node: initiate network connections and start the state machine.
        """
        # Open Solipsis main port
        sender = self.node_connector.SendMessage
        self.state_machine.Init(sender, self.remote_control, bootup_entities)
        try:
            self.node_connector.Start(self.port)
        except Exception, e:
            print str(e)
            self.reactor.stop()
            sys.exit(1)
        self.reactor.addSystemEventTrigger('during', 'shutdown', self.node_connector.Stop)

        # Setup the initial state
        if self.params.as_seed:
            self.state_machine.ImmediatelyConnect()
        else:
            self.state_machine.TryConnect()
        self.reactor.addSystemEventTrigger('before', 'shutdown', self.state_machine.Close)
        self.reactor.addSystemEventTrigger('after', 'shutdown', self.state_machine.DumpStats)

        # Start remote controller
        if not self.params.bot:
            c = controller.xmlrpc.Controller(self.reactor, self.params, self.remote_control)
            c.Start(self.control_port)
            self.reactor.addSystemEventTrigger('before', 'shutdown', c.Stop)


class Bootstrap(object):
    def __init__(self, reactor, params):
        """
        Initialize the bootstrap object and all necessary objects.
        Also does the local IP address discovery.
        """
        self.reactor = reactor
        self.params = params
        self.pool = []

    def Run(self):
        """
        Initiate the network connections and launch the main loop.
        """
        # Enter event loop
        self.reactor.callLater(0, self.LaunchPool)
        self.reactor.run()

    def LaunchPool(self):
        """
        Launch the pool of local nodes.
        """
        deferreds = []
        if self.params.pool:
            # Prepare a pool of nodes
            for i in range(self.params.pool):
                p = NodeLauncher(self.reactor, self.params)
                self.pool.append(p)
                deferreds.append(p.Prepare(i))
        else:
            # Prepare a single node
            p = NodeLauncher(self.reactor, self.params)
            self.pool.append(p)
            deferreds.append(p.Prepare())

        # Startup entities are saved in a file
        if not self.params.as_seed:
            bootup_entities = self._ParseEntitiesFile(self.params.entities_file)
        else:
            bootup_entities = []

        def _succeed(results):
            # Build the list of local addresses once they are known
            addresses = []
            for r in results:
                host, port = r[1]
                print "local address is %s:%d" % (host, port)
                addresses.append((host, port))
            for p in self.pool:
                self.reactor.callLater(0, p.Launch, bootup_entities or addresses)

        def _fail(failure):
            raise Exception(failure)

        # We must wait for all addresses to be known
        # before we can really launch the nodes
        d = defer.DeferredList(deferreds, fireOnOneErrback=True, consumeErrors=True)
        d.addErrback(_fail)
        d.addCallback(_succeed)


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

