import sys
import logging

from solipsis.util.parameter import Parameters
from solipsis.util.geometry import Position
from solipsis.util.address import Address
from solipsis.util.exception import *

from entity import Entity


class Node(Entity):
    count = 0

    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params

        if not params.bot:
            # TODO: initialize XMLRPC
            pass

        id_ = self.CreateId()
        position = Position(params.pos_x, params.pos_y)
        address = Address(params.host, params.port)

        # call parent class constructor
        Entity.__init__(self, id_=id_, position=position, orientation=params.orientation,
                        calibre=params.calibre, pseudo=params.pseudo, address=address)

        # maximum expected number of neighbours.
        self.expected_peers = params.expected_neighbours

        # our IP address or 'localhost' if not specified in config file
        self.host = params.host

        self.alive = True
        self.logger = logging.getLogger('root')
        self.logger.debug('node started')

        # Set world size in Geometry class
#         Geometry.SIZE = params.world_size


    def CreateId(self):
        # TODO: reasonable ID generation and attribution
        id_ = "%s:%d_%d" % (self.params.host, self.params.port, Node.count)
        Node.count += 1
        return id_

#     def SetPosition(self, position):
#         super(Node, self).setPosition(position)
#         self.peersManager.recalculate()

