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

from solipsis.util.parameter import Parameters
from solipsis.util.position import Position
from solipsis.util.address import Address
from solipsis.util.exception import *

from solipsis.util.entity import Entity


class Node(Entity):
    count = 0

    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params

        id_ = self.CreateId()
        position = Position((params.pos_x, params.pos_y, 0))
        address = Address(params.host, params.port)

        # call parent class constructor
        Entity.__init__(self, id_=id_, position=position, pseudo=params.pseudo, address=address)

        # maximum expected number of neighbours.
        self.expected_peers = params.expected_neighbours

        #~ # our IP address or 'localhost' if not specified in config file
        #~ self.host = params.host
        self.alive = True

    def CreateId(self):
        # TODO: reasonable ID generation and attribution
        id_ = "%s:%d_%d" % (self.params.host, self.params.port, Node.count)
        Node.count += 1
        return id_
