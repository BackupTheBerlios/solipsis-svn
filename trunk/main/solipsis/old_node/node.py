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
## -----                           node.py                                   -----
## ------------------------------------------------------------------------------


import sys, os, traceback
import logging

from solipsis.util.parameter import Parameters
from solipsis.util.geometry import Geometry, Position
from solipsis.util.address import Address
from solipsis.util.container import NotificationQueue

from solipsis.util.exception import *

from solipsis.node.entity import Entity
from solipsis.node.peer import PeersManager
from solipsis.node.peerevent import PeerEvent, PeerEventParser
from solipsis.node.controlevent import ControlEvent, ControlEventParser
from solipsis.node.xmlrpcconnector import XMLRPCConnector
from solipsis.node.udpconnector import UDPConnector
from solipsis.node.event import EventFactory
from solipsis.node.peerevent import PeerEventFactory
from solipsis.node.controlevent import ControlEventFactory
import state
import periodic

class Node(Entity):


    def __init__(self, params):
        """ All informations about this node:
        host --> ip if the node, network_port, GUI_port, posX, posY, ar, ca,
        ori --> a point,
        exp --> expected number of neighbour, pseudo"""

        self.params=params

        # event queue, used for inter-thread communication
        self.events = NotificationQueue()
        self.connectors = []

        EventFactory.init(self)
        EventFactory.register(PeerEventFactory.TYPE, PeerEventFactory())
        EventFactory.register(ControlEventFactory.TYPE, ControlEventFactory())

        # network communication with peers is handled by this object
        self.peerConnector = UDPConnector(PeerEventParser(), self.events, params)
        self.connectors.append(self.peerConnector)

        if (not params.bot):
            self.controlConnector = XMLRPCConnector(ControlEventParser(), self.events, params)
            self.connectors.append(self.controlConnector)
        else:
            self.controlConnector = None

        id_ = self.createId()
        position = Position(params.pos_x, params.pos_y)
        address = Address(params.host, params.port)

        # call parent class constructor
        Entity.__init__(self, id_, position, params.orientation,
                        params.awareness_radius, params.calibre, params.pseudo,
                        address)

        # maximum expected number of neighbours.
        self.exp = params.expected_neighbours

        # our IP address or 'localhost' if not specified in config file
        self.host = params.host

        self.alive = True
        self.logger = logging.getLogger('root')
        self.logger.debug('node started')
        # manage all peers
        #peersParams = params.getPeersParams()
        self.peersManager = PeersManager(self, params)

        # set world size in Geometry class
        Geometry.SIZE = params.world_size

        # periodic tasks
        self.periodic = []

        self.state = None
        self.setState(state.NotConnected())


    def createId(self):
        return self.params.host + ':' + str(self.params.port)

    def getPeersManager(self):
        return self.peersManager

    def setExpectedPeers(self, nbPeers):
        """ Set the expected numbetr of peers for the node"""
        self.exp = nbPeers
        self.peersManager.setExpectedPeers(nbPeers)

    def setState(self, stateObject):
        """ Change the current state of the node."""
        self.state = stateObject
        stateObject.setNode(self)
        stateObject.setLogger(self.logger)
        stateObject.activate()

    def dispatch(self, event):
        """ Send an event.
        event : the event to send.
        """
        connector = None
        event_type = event.getType()
        if event_type == PeerEvent.TYPE:
            connector = self.peerConnector
        elif event_type == ControlEvent.TYPE:
            connector = self.controlConnector
        else:
            raise InternalError('Unknown event type ' + event_type)

        if connector is not None:
            connector.send(event)

    def exit(self):
        """ stop the node and exit
        """
        # we do not need to stop the controlConnector. The controlConnector
        # stopped after sending us the exit message
        # --> self.controlConnector.stop() not needed !

        # wait for the other threads before exiting
        for c in self.connectors:
            if c.isAlive():
                c.stop()
                c.join()

        self.alive = False

    def startPeriodicTasks(self):
        """ Start all the periodic tasks of this node, like sending heartbeats"""
        hb = periodic.Heartbeat(self)
        self.periodic.append(hb)
        hb.start()

    def mainLoop(self):
        """ Main loop of the program """

        # start control connector
        for c in self.connectors:
            c.start()

        while self.alive:
            # Check our connectors are still there
            for c in self.connectors:
                if not c.isAlive():
                    print "connector aborted"
                    self.exit()
                    raise ConnectorError()

            self.events.acquire()
            # no events to process - wait for a notification from other threads
            if self.events.empty():
                self.events.wait()

            # We can immediately release the lock: we know that there is an item available
            # because this is the only thread that consumes items from the queue.
            # If other threads can consume item then we must first get the item then
            # release the lock
            self.events.release()

            # process one event in queue
            event = self.events.get()
            request = event.getRequest()

            try:
                fun = self.state.__getattribute__(request)
            except:
                self.logger.debug("unknown request "+ request)
            try:
                fun(event)
            except:
                exception_type, value, tb = sys.exc_info()
                self.logger.debug(exception_type)
                self.logger.debug(value)
                stack_trace = traceback.format_tb(tb)
                self.logger.debug(stack_trace)


        self.logger.debug("end of main loop")

