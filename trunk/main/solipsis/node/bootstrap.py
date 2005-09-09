# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>

import sys
import logging
import random

import twisted.internet.defer as defer
# For centralized statistics
from twisted.web.client import getPage

from solipsis.util.position import Position
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
    """
    This class prepares and launches a node according to the parameters
    specified by the user.
    """

    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params

    def Prepare(self, pool_num=0):
        """
        Prepare the node and return the assigned (host, port) tuple.
        """
        self.pool_num = pool_num
        self.host = self.params.host or "127.0.0.1"
        self.port = self.params.port + pool_num
        node = Node(self.reactor, self.params)
        self.logger = logging.getLogger("peer.port_%d" % self.port)
        self.logger.setLevel(logging.DEBUG)
        self.state_machine = StateMachine(self.reactor, self.params, node, self.logger)
        self.node_connector = NodeConnector(self.reactor, self.params, self.state_machine, self.logger)
        self.remote_control = RemoteControl(self.reactor, self.params, self.state_machine, self.logger)

        # IP address discovery:
        # the successive discovery methods are specified in the configuration file.
        # Each is handled by a given file in the discovery/ subdirectory.
        discovery_methods = list(self.params.discovery_methods)
        discovery_deferred = defer.Deferred()

        def _try_next(failure=None):
            # Try next discovery method
            try:
                method = discovery_methods[0]
            except IndexError:
                self.reactor.fireSystemEvent('shutdown')
                sys.exit(1)
            discovery = _import('solipsis.node.discovery.' + method)
            d = discovery.DiscoverAddress(self.port, self.reactor, self.params)
            d.addCallback(_found_public_addr)
            d.addErrback(_fail)

        def _found_public_addr(address):
            # Discovery succeeded
            self.host, self.port = address
            node.address = Address(self.host, self.port)
            print "public address is %s:%d" % (self.host, self.port)
            _find_private_addr()

        def _fail(failure):
            # Discovery failed => try next discovery method
            print discovery_methods[0], "discovery failed:", failure.getErrorMessage()
            discovery_methods.pop(0)
            _try_next()

        def _find_private_addr():
            discovery = _import('solipsis.node.discovery.local')
            d = discovery.DiscoverAddress(self.port, self.reactor, self.params)
            d.addCallback(_found_private_addr)

        def _found_private_addr(address):
            host, port = address
            if host != self.host or port != self.port:
                node.address.private_host = host
                node.address.private_port = port
                print "private address is %s:%d" % (host, port)
            discovery_deferred.callback((self.host, self.port))

        if self.params.host.strip():
            _found_public_addr((self.params.host.strip(), self.params.port))
        else:
            _try_next()
        return discovery_deferred


    def Launch(self, bootup_entities):
        """
        Launch the node: initiate network connections and start the state machine.
        """
        # Open Solipsis main port
        self.state_machine.Init(self.node_connector, self.remote_control, bootup_entities)
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

        # Start remote controller(s)
        if not self.params.bot:
            for controller_name in self.params.controllers:
                try:
                    c = _import('solipsis.node.controller.' + controller_name)
                except ImportError, e:
                    print str(e)
                    self.reactor.stop()
                    sys.exit(1)
                c = c.Controller(self.reactor, self.params, self.remote_control)
                c.Start(self.pool_num)
                self.reactor.addSystemEventTrigger('after', 'shutdown', c.Stop)


class Bootstrap(object):
    """
    This class handles the launching of the node or pool of nodes
    according to parameters given by the user.
    """

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

        # Startup entities are loaded from a file
        if not self.params.as_seed:
            bootup_entities = self._ParseEntitiesFile(self.params.entities_file)
        else:
            bootup_entities = []

        def _succeed(results):
            # Build the list of local addresses once they are known
            addresses = []
            for ok, result in results:
                if ok:
                    host, port = result
                    addresses.append((host, port))
            for p in self.pool:
                self.reactor.callLater(0, p.Launch, bootup_entities or addresses)
            # Send statistics
            if self.params.send_stats:
                getPage('http://solipsis.netofpeers.net/stat/index.php?z=1')

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
