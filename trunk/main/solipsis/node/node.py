import sys, os, traceback
import logging

from solipsis.util.parameter import Parameters
from solipsis.util.geometry import Geometry, Position
from solipsis.util.address import Address
from solipsis.util.container import NotificationQueue

from solipsis.util.exception import *

from entity import Entity
import state
import periodic

class Node(Entity):
    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params

        if not params.bot:
            # TODO: initialize XMLRPC
            pass

        id_ = self.createId()
        position = Position(params.pos_x, params.pos_y)
        address = Address(params.host, params.port)

        # call parent class constructor
        Entity.__init__(self, id_, position, params.orientation,
                        params.awareness_radius, params.calibre, params.pseudo,
                        address)

        # maximum expected number of neighbours.
        self.expected_peers = params.expected_neighbours

        # our IP address or 'localhost' if not specified in config file
        self.host = params.host

        self.alive = True
        self.logger = logging.getLogger('root')
        self.logger.debug('node started')

        # manage all peers
        self.peersManager = PeersManager(self, params)

        # set world size in Geometry class
        Geometry.SIZE = params.world_size

        self.state = None
        self.setState(state.NotConnected())

    def CreateId(self):
        # TODO: reasonable ID generation and attribution
        return self.params.host + ':' + str(self.params.port)

    def SetPosition(self, position):
        super(Node, self).setPosition(position)
        self.peersManager.recalculate()

    def MainLoop(self):
        self.reactor.run()
