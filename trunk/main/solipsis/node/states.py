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

"""
This module contains the Finite State Machine (FSM)
that implements the Solipsis protocol.

There is a base class for every state called State,
and each distinct state is represented by a class derived
from State:

    - class Locating (State)
    - class NotConnected (State)
    - etc.
"""

import logging


class State(object):
    """
    Base class for all states recognized by the Solipsis state machine.
    """


class NotConnected(State):
    """
    State NotConnected: Initial state of the node.

    The node is not connected to any entity, and it has not yet tried to
    gather any information about the world.

    Thus the only possible action is to to MOVE to an absolute position,
    which will trigger the Locating - Scanning - Connecting algorithm.
    """
    expected_peer_messages = []
    expected_control_messages = ['MOVE', 'KILL', 'SET']


class Locating(State):
    """ TRACKING: The node has attempted a first connection to the world and
    is now running the find-nearest-neighbour algorithm.

    This means the node is expecting a BEST message from its latest peer.
    """
    expected_peer_messages = ['NEAREST', 'BEST', 'HEARTBEAT']
    expected_control_messages = ['MOVE', 'KILL', 'SET']


class Scanning(State):
    """
    State Scanning: The node has found its place in the world. It is asking its
    first neighbours to discover other neighbours around its target positions.
    """
    expected_peer_messages = ['NEAREST', 'BEST', 'AROUND', 'HEARTBEAT', 'FINDNEAREST']
    expected_control_messages = ['MOVE', 'KILL', 'SET']


class Connecting(State):
    """
    State Connecting: The node has found all the neigbours around its target position.
    It is now attempting to connect to these peers.
    """


class EarlyConnecting(State):
    """
    State EarlyConnecting: The node first connects to a bunch of initial peers,
    before launching the proper locating procedure.
    This state is a special state only used for the world creation.
    """
    expected_peer_messages = ['HELLO', 'CONNECT', 'CLOSE', 'HEARTBEAT']
    expected_control_messages = ['MOVE', 'KILL', 'SET']


class Idle(State):
    """
    State Idle: the node has a stable position and is fully connected to its local neighborhood.
    """


class LostGlobalConnectivity(State):
    """
    State LostGlobalConnectivity: the node has lost its global connectivity.
    """

