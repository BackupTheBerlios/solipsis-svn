
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
    def __init__(self, state_machine):
        self.state_machine = state_machine
        self.logger = logging.getLogger("root")


class NotConnected(State):
    """ NOT CONNECTED: Initial state of the node.

    The node is not connected to any entity.
    The only allowed action is to JUMP to an absolute position in the world.
    The JUMP action will trigger a Solipsis connection to a first peer, and
    then the find-nearest-neighbour algorithm so as to connect to the right peers
    according to the desired JUMP position.
    """

    expected_peer_messages = []
    expected_control_messages = ['MOVE', 'KILL', 'SET']


class Locating(State):
    """ TRACKING: The node has attempted a first connection to the world and
    is now running the find-nearest-neighbour algorithm.

    This means the node is expecting a BEST message from its latest peer.
    """

    # maximum number of times we will try to connect
    MAX_CONNECTIONS_ATTEMPTS = 5

    expected_peer_messages = ['NEAREST', 'BEST']
    expected_control_messages = ['MOVE', 'KILL', 'SET']

#     def __init__(self):
#         self.expectedMessages = ['NEAREST', 'BEST', 'TIMER', 'KILL', 'MOVE', 'SET']
#         self.connectionAttempts = 0
#         # timer object associated with the curent findnearest request - needed
#         # to cancel the timer when we receive a response
#         self.startTimer()
#
#     def activate(self):
#         pass
#
#     def NEAREST(self, event):
#         super(Locating, self).NEAREST(event)
#         self.startTimer()
#
#     def TIMER(self, event):
#         """ Timeout while waiting for an answer for a FINDNEAREST request """
#         self.connectionAttempts += 1
#
#         # connection failed
#         if self.connectionAttempts > self.MAX_CONNECTIONS_ATTEMPTS:
#             self.connectionError()
#
#         # retry connecting
#         manager = self.node.getPeersManager()
#         peer = manager.getRandomPeer()
#         self.sendFindNearest(peer.getAddress())
#         self.startTimer()

class Scanning(State):
    """ SCANNING: The node has found its place in the world. It is asking its
    neighbours to notify it of other neighbours so as to have a complete
    knowledge of its the local neighborhood.
    """

    expected_peer_messages = ['NEAREST', 'AROUND']
    expected_control_messages = ['MOVE', 'KILL', 'SET']

#     def __init__(self):
#         self.expectedMessages = ['AROUND', 'NEAREST', 'KILL', 'MOVE', 'SET']
#         self.best = None
#         self.neighbours = []
#         self.startTimer()
#
#     def activate(self):
#         self.logger.debug('Scanning')
#
#     def setBestPeer(self, peer):
#         """ Store information on who we currently think is the closest peer to
#         our target position.
#
#         peer : the best peer (the closest to our target position)"""
#         # store this peer
#         self.best = peer
#         # add this peer to the list of the peers around our target position
#         self.addPeerAround(peer)
#
#     def addPeerAround(self, peer):
#         self.neighbours.append(peer)
#
#     def NEAREST(self, event):
#         """ While scanning around our target a position, a peer informs us that
#         there exists a peer that is closer than our current best.
#         """
#         peerPos = event.getArg(protocol.ARG_REMOTE_POSITION)
#
#         # check if this peer is closer than our current best
#         currentBestDistance = Geometry.distance(self.best.getPosition(),
#                                                 self.node.getPosition())
#         newDist = Geometry.distance(peerPos, self.node.getPosition())
#         if newDist < currentBestDistance:
#             super(Scanning,self).NEAREST(event)
#             self.node.setState(Locating())
#
#     def TIMER(self, event):
#         """ We have a timeout for our last queryaround message """
#         # retry going around from our current best peer
#         import exceptions
#         raise exceptions.NotImplementedError()


class Connecting(State):
    """ CONNECTING: The node has found all the neigbours around its position.
    It is now attempting to connect to these peers.
    """

    # in the connecting state we increase our awareness radius in a linear way
    PERCENTAGE_AR_INCREASE = 0.3
    # maximum number of times we will try to incerease our awareness radius
    MAX_AR_INCREASE_ATTEMPTS = 10

    def __init__(self):
        self.expectedMessages = ['CONNECT', 'SERVICE', 'TIMER']
        self.nbArIncrease = 0
        self.startTimer()

    def activate(self):
        pass

    def CONNECT(self, event):
        super(Connecting, self).CONNECT(event)
        mng = self.node.getPeersManager()

        # we have now reached our number of expected neighbours
        if not mng.hasTooFewPeers():
            self.timer.cancel()
            if not mng.hasGlobalConnectivity():
                self.searchPeers()
                self.node.setState(NoGlobalConnectivity())
            else:
                # start periodic tasks and go to Idle state
                self.node.startPeriodicTasks()
                self.node.setState(Idle())

    def TIMER(self, event):
        """ The timer expired."""
        mng = self.node.getPeersManager()
        # we got 0 responses: we have a big problem !
        if mng.getNumberOfPeers() == 0:
            self.connectionError()
        elif self.nbArIncrease < Connecting.MAX_AR_INCREASE_ATTEMPTS:
            # first time we increase our AR, try to guess a good value
            if self.nbArIncrease == 0:
                self.node.setAwarenessRadius(mng.getMedianAwarenessRadius())
            else:
                # increase awareness radius
                ar = self.node.getAwarenessRadius()
                factor = 1 + Connecting.PERCENTAGE_AR_INCREASE
                self.node.setAwarenessRadius(int(ar*factor))

            # notify our peers
            self.sendUpdates()
            # relaunch a timer
            self.startTimer()
            self.nbArIncrease = self.nbArIncrease + 1
        else:
            self.connectionError()

class Idle(State):
    """ IDLE: the node has a stable position and is fully connected to its local neighborhood.
    """

    def __init__(self):
        self.expectedMessages = ['HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']

    def activate(self):
        pass


class NoGlobalConnectivity(State):
    """ Our global connectivity rule is not satisfied """
    def __init__(self):
        self.expectedMessages = ['FOUND', 'HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']
        self.startTimer()

    def activate(self):
        pass

    def FOUND(self, event):
        """ an entity detected in an empty sector
        reception of message: FOUND"""
        peer = event.createRemotePeer()
        manager = self.node.getPeersManager()
        id_ = peer.getId()
        factory = EventFactory.getInstance(PeerEvent.TYPE)

        # verify that new entity is neither self neither an already known entity.
        if id_ != self.node.getId() and not manager.hasPeer(id_):
            hello = factory.createHELLO()
            hello.setRecipientAddress(peer.getAddress())
            self.node.dispatch(hello)



    def TIMER(self, event):
        """ Timeout : we still don't have our GC"""
        # restart the timer
        self.startTimer()
        # search peers
        self.searchPeers()

class NotEnoughPeers(State):
    """ We do NOT have enough peers."""
    def __init__(self):
        self.expectedMessages = ['FOUND', 'HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']
        self.startTimer()

    def activate(self):
        pass

    def CONNECT(self, event):
        super(NotEnoughPeers, self).CONNECT(event)
        mng = self.node.getPeersManager()

        # we have now reached our number of expected neighbours
        if not mng.hasTooFewPeers():
            self.timer.cancel()
            self.node.setState(Idle())

    def TIMER(self, event):
        """ Timeout : we still don't have enough peers"""
        self.startTimer()
        self.updateAwarenessRadius()



class NotEnoughPeersAndNoGlobalConnectivity(State):
    """ We don't have enough peers and the Global connectivity rule is
    not satisfied"""
    def __init__(self):
        self.expectedMessages = ['FOUND', 'HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']
        self.startTimer()

    def activate(self):
        self.logger.debug('NotEnoughPeersAndNoGlobalConnectivity')

    def CONNECT(self, event):
        super(Connecting, self).CONNECT(event)
        mng = self.node.getPeersManager()

        # we have now reached our number of expected neighbours
        if not mng.hasTooFewPeers():
            self.timer.cancel()
            # our GC is also OK go to Idle state
            if mng.hasGlobalConnectivity():
                self.node.setState(Idle())
            # GC is still NOK : go to NoGlobalConnectivity state
            else:
                self.searchPeers()
                self.node.setState(NoGlobalConnectivity())
        # we still don't have enough peers
        else:
            # but now our GC is OK : go to state NotEnoughPeers
            if mng.hasGlobalConnectivity():
                self.timer.cancel()
                self.updateAwarenessRadius()
                self.node.setState(NotEnoughPeers())

    def TIMER(self, event):
        """ Timeout : we still don't have enough peers"""
        self.startTimer()
        self.updateAwarenessRadius()
        self.searchPeers()

class TooManyPeers(State):
    """ We have too many peers """
    def __init__(self):
        self.expectedMessages = ['FOUND', 'HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']
        self.startTimer()

    def TIMER(self, event):
        """ Timeout : check if we still have too many peers peers"""
        manager = self.node.getPeersManager()
        factory = EventFactory.getInstance(PeerEvent.TYPE)

        while manager.getNumberOfPeers() > manager.getExpectedPeers():
            peer = manager.getWorstPeer()
            close = factory.createCLOSE()
            close.setRecipientAddress(peer.getAddress())
            self.node.dispatch(close)
            self.removePeer(peer)

        self.updateAwarenessRadius()
        self.node.setState(Idle())

