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
import math
import random

from solipsis.util.exception import *
from solipsis.util.geometry import Position
from peer import Peer
import protocol
import states
from topology import Topology
from delayedcaller import DelayedCaller


# Forward compatibility with built-in "set" types
try:
    set
except:
    from sets import Set as set


class StateMachine(object):
    """
    Finite State Machine of the Solipsis protocol.
    This is where all the interesting stuff happens.
    """
    world_size = 2**128

    # It is safer not to set this greater than 1
    teleportation_flood = 1
    neighbour_tolerance = 0.3
    peer_neighbour_ratio = 2.0

    # Various retry delays
    scanning_period = 4.0
    connecting_period = 4.0
    early_connecting_period = 3.0
    gc_check_period = 4.0
    population_check_period = 5.0

    # Various timeouts
    gc_trials = 3
    locating_timeout = 5.0
    early_connecting_trials = 3
    locating_trials = 3
    scanning_trials = 3
    connecting_trials = 3

    # Time during which we request to send detects on a HELLO
    # after having moved
    move_duration = 3.0

    # These are all the message types accepted from other peers.
    # Some of them will only be accepted in certain states.
    # The motivation is twofold:
    # - we don't want to answer certain queries if our answer may be false
    # - we don't want to process answers to questions we didn't ask
    accepted_peer_messages = {
        'AROUND':       [states.Scanning, states.Connecting],
        'BEST':         [states.Locating, states.Scanning],
        'CONNECT':      [],
        'CLOSE':        [],
        'DETECT':       [],
        'FINDNEAREST':  [states.Scanning, states.Connecting, states.Idle, states.LostGlobalConnectivity],
        'FOUND':        [],
        'HEARTBEAT':    [],
        'HELLO':        [],
        'NEAREST':      [states.Locating, states.Scanning],
        'QUERYAROUND':  [states.Idle],
        'SEARCH':       [states.Idle],
        'UPDATE':       [],
    }

    def __init__(self, reactor, params, node, logger=None):
        """
        Initialize the state machine.
        """
        self.reactor = reactor
        self.params = params
        self.node = node
        self.topology = Topology()
        self.logger = logger or logging.getLogger("root")
        self.parser = protocol.Parser()

        # Expected number of neighbours (in awareness radius)
        self.expected_neighbours = params.expected_neighbours
        self.min_neighbours = int(round((1.0 - self.neighbour_tolerance) * self.expected_neighbours))
        self.max_neighbours = int(round((1.0 + self.neighbour_tolerance) * self.expected_neighbours))
        # Max number of connections (total)
        self.max_connections = int(self.expected_neighbours * self.peer_neighbour_ratio)

        self.caller = DelayedCaller(self.reactor)
        self.peer_sender = None
        # Dispatch tables
        self.peer_dispatch_cache = {}
        self.state_dispatch = {}

        # Statistics
        self.received_messages = {}
        self.sent_messages = {}

        self.Reset()

    def Reset(self):
        self.state = None
        self.peer_dispatch = {}

        self.moved = False
        # Id's of the peers encountered during a FINDNEAREST chain
        self.nearest_peers = set()
        # Peers discovered during a QUERYAROUND chain
        self.future_topology = None
        # BEST peer discovered at the end of a FINDNEAREST chain
        self.best_peer = None
        self.best_distance = 0.0

        # Delayed calls
        self.peer_timeouts = {}
        self.caller.Reset()

        self.topology.Reset(origin=self.node.position.getCoords())

    def Init(self, peer_sender, event_sender, bootup_addresses):
        """
        Initialize the state machine. This is mandatory.
        """
        self.peer_sender = peer_sender
        self.event_sender = event_sender
        self.bootup_addresses = bootup_addresses

    def Close(self):
        """
        Close all connections and finalize stuff.
        """
        self._CloseCurrentConnections()
        self.Reset()

    def SetState(self, state):
        """
        Change the current state of the state machine.
        The 'state' parameter must be an instance of one
        of the State subclasses.
        """
        old_state = self.state
        self.state = state
        _class = state.__class__
        try:
            self.peer_dispatch = self.peer_dispatch_cache[_class]
        except KeyError:
            # Here we build a cache for dispatching peer messages
            # according to the current state.
            d = {}
            # We restrict message types according both to:
            # 1. expected messages in the given state
            # 2. accepted states for the given message type
            try:
                messages = state.expected_peer_messages
            except AttributeError:
                messages = self.accepted_peer_messages.keys()
            for request in messages:
                l = self.accepted_peer_messages[request]
                if len(l) == 0 or _class in l:
                    d[request] = getattr(self, 'peer_' + request)
            self.peer_dispatch = d
            self.peer_dispatch_cache[_class] = d
        if _class != old_state.__class__:
            # Discard old timers
            self.caller.Reset()
            # Call state initialization function
            try:
                func = self.state_dispatch[_class]
            except:
                func = getattr(self, 'state_' + _class.__name__, None)
                self.state_dispatch[_class] = func
            if func is not None:
                func()
            # Notify controller(s)
            self.event_sender.event_StatusChanged(self.GetStatus())

    def InState(self, state_class):
        """
        Returns True if the current state is an instance of the given class.
        """
        return isinstance(self.state, state_class)

    def PeerMessageReceived(self, request, args):
        """
        Called by the network routines when a proper Solipsis message is received.
        """
        try:
            func = self.peer_dispatch[request]
        except:
            self.logger.info("Ignoring unexpected message '%s' in state '%s'" % (request, self.state.__class__.__name__))
        else:
            func(args)
            try:
                self.received_messages[request] += 1
            except KeyError:
                self.received_messages[request] = 1
            # Heartbeat handling
            try:
                id_ = args.id_
            except AttributeError:
                pass
            else:
                if id_ in self.peer_timeouts:
                    self.peer_timeouts[id_].RescheduleCall('msg_receive_timeout')

    def DumpStats(self):
        requests = self.sent_messages.keys()
        requests.extend([k for k in self.received_messages.keys() if k not in requests])
        requests.sort()
        self._Verbose("\n... Message statistics ...")
        for r in requests:
            self._Verbose("%s: %d sent, %d received" % (r, self.sent_messages.get(r, 0), self.received_messages.get(r, 0)))


    #
    # Methods called when a new state is entered
    #
    def state_NotConnected(self