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
from threading import Thread
import logging

from solipsis.util.container import NotificationQueue

class Connector(Thread):
    """ Generic class for connecting to another component(peer or navigator) """
    def __init__(self, parser, eventQueue):
        """ Constructor
        parser : the Parser object used to parse the events going in and out of this
        connector
        eventQueue : queue used to communicate with other thread. The Connector
        fills this queue with events. Other threads are responsible for reading and
        removing events from this queue
        """
        Thread.__init__(self)

        # Event queue used to communicate with other threads
        # these events comes from other entities through this connector
        # and will be processed by the node
        self.incoming = eventQueue

        # Message to send queue
        # the node has created an event that will be sent using this connector
        # to another entity
        self.outgoing = NotificationQueue()

        # this flag is set to True when we want to stop this thread
        self.stopThread = False

        # Parser object
        self.parser = parser

        # logger
        self.logger = logging.getLogger('root')


    def stop(self):
        """ Stop the network thread
        """
        self.stopThread = True

    def setParser(self, parser):
        """ Set the connector type.
        parser : the Parser object used to parse the events going through this connector
        """
        self.parser = parser


