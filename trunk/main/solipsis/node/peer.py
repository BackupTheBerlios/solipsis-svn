## SOLIPSIS Copyright (C) France Telecom

## This file is part of SOLIPSIS.

##    SOLIPSIS is free software; you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as published by
##    the Free Software Foundation; either version 2.1 of the License, or
##    (at your option) any later version.

##    SOLIPSIS is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU Lesser General Public License for more details.

##    You should have received a copy of the GNU Lesser General Public License
##    along with SOLIPSIS; if not, write to the Free Software
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

## ------------------------------------------------------------------------------
## -----                           Peer.py                                -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module defines the class for a neighbor.
##   A neighbor is an entity with which we are able to communicate.
##   This module provides all methods for the modifications of any variable
##   characteristic of an entity.
##   These modifications are capted by the Network module.
##
## ******************************************************************************

import random
import string, time, logging, math

from solipsis.util.exception import *

from entity import Entity


class Peer(Entity):

    def __init__(self, *args, **kargs):
        """ Create a new Entity and keep information about it"""

        # Call parent class constructor
        super(Peer, self).__init__(*args, **kargs)

        # TODO: initialize this from protocol message
        self.keepalive_duration = 30

        # Time of latest messages received/sent
        self.last_received_message = 0
        self.last_sent_message = 0

        # Services provided by entity
        # {id_service: [desc_service, host, port], ...}
        self.services = {}

