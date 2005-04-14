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
from threading import Thread, Timer
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer

from solipsis.node.event import EventFactory
from solipsis.node.controlevent import ControlEvent
from solipsis.node.connector import Connector
from solipsis.util.container import NotificationQueue
from solipsis.util.exception import NotImplementedError
from solipsis.util.geometry import Position

class XMLRPCConnector(Connector):

    def __init__(self, parser, eventQueue, params):
        """ Constructor.
        parser : the Parser object used to parse the events going through this connector
        fills this queue with events. Other threads are responsible for reading and
        removing events from this queue
        netParams : initialization parameters of this class -
        a list [ buffer_size, logger_object ]
        """
        Connector.__init__(self, parser, eventQueue)
        self.host = params.control_host
        self.controlPort = params.control_port
        self.notificationPort = params.notif_port
        # XML/RPC server used for receiving control orders
        self.controlChannel = XMLRPCControlChannel(self)
        # XML/RPC server used for sending notification to the controller
        self.notificationChannel = XMLRPCNotificationChannel(self)

    def run(self):
        """ Start 2 XML/RPC servers one for receiving control message from the
        controller and another to send both reply to queries and asynchronous events
        coming from the network (e.g. this 2nd channel is used to notify the
        controller when a new node is discovered) """

        self.notificationChannel.start()
        self.logger.info("XMLRPC Connector started")

        while not self.stopThread:
            self.controlChannel.server.handle_request()

        # set the STOP flag of the notification thread
        #self.notificationChannel.stopThread = True

        # we need to send back the kill event to the controller because he is waiting
        # for a reply from the notification thread
        # (the call to XMLRPCNotificationChannel.get is blocking)
        # TODO
        # self.send(Event(["kill"]))

        # wait for child thread before exiting
        self.notificationChannel.join()
        self.logger.info("End of control thread")

    def send(self, notification):
        """ Send a notification to the controller
        notification : an Event object
        """
        self.notificationChannel.send(notification)
        self.logger.debug(str(notification))

class XMLRPCNotificationChannel(Thread):
    """ Comunication channel used by the node to send notification to its controller.
    It is a one-way communication channel from the node to the controller.
    The controller calls the get method, and blocks waiting for a reply. Whenever a
    new event needs to be sent to the controller, this message is sent back in reply
    to the get method call and the controller calls back the get method.
    """

    def __init__(self, connector):
        """ Constructor.
        host : ip address of the node
        port : port used by this XML/RPC server"""
        self.parser = connector.parser
        Thread.__init__(self)
        self.host = connector.host
        self.port = connector.notificationPort
        self.server =  SimpleXMLRPCServer((self.host, self.port))
        self.server.register_instance(self)

        # Message to send queue
        self.outgoing = connector.outgoing
        self.connector = connector

    def run(self):
        while not self.connector.stopThread:
            self.server.handle_request()

    def get(self):
        """ Wait for notification from the node main thread and send back events to the
        controller. The controller calls the get method and is notified when a network
        event occurs."""
        # get the lock
        self.outgoing.acquire()
        # nothing to send, just wait
        if self.outgoing.empty():
            time.sleep(0.020)
            self.outgoing.wait(4.0)

        # the main thread called the notify method to awaken this thread
        # release the lock and send back the message to the controller.
        self.outgoing.release()

        l = []
        while not self.outgoing.empty():
            e = self.outgoing.get()
            response = self.parser.getData(e)
            l.append(response)
        print "*** %d notifications ... ***" % len(l)
        print "\n".join([str(_r) for _r in l])
        return l

    def send(self, notification):
        """ Send a message to the controller
        notification: an Event object
        """
        self.outgoing.put(notification)


class XMLRPCControlChannel(object):
    """ Channel used for receiving orders from a navigator

    """
    def __init__(self, connector):
        self.parser = connector.parser
        self.host = connector.host
        self.port = connector.controlPort
        self.server = SimpleXMLRPCServer((self.host, self.port))
        self.server.register_instance(self)
        self.incoming = connector.incoming
        # standard response for non get queries
        # The real event processing is asynchronous (in the main thread),
        # so we just send back this dummy value to the navigator
        self.ok = "1"
        self.connector = connector

    def addService(self, srvId, srvDesc, srvConnectionString):
        """ add a new service to the node. """
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        addSrv = factory.createADDSERVICE(srvId, srvDesc, srvConnectionString)
        self.incoming.put(addSrv)

        return self.ok

    def delService(self, srvId):
        """ Remove a service
        srvId : id of the service to remove
        Return : OK """
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        rmSrv = factory.createDELSERVICE(srvId)
        self.incoming.put(rmSrv)
        return self.ok


    def update(self, var, value):
        """ Update a caracteristic of the node
        var : the type of information to update, 'AR', 'POS', 'ORI', 'PSEUDO'
        value : new value
        """
        controlEvent = self.parser.createEvent("update", var, value)
        self.incoming.put(controlEvent)
        return self.ok

    def getNodeInfo(self):
        """ Return all the caracteristics of the node
        [id, positionX, positionY, AR, CA, pseudo, orientation ]
        """
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        controlEvent = factory.createGETNODEINFO()
        self.incoming.put(controlEvent)
        return self.ok

    def getPeerInfo(self, id):
        """ Return all the caracteristics of a peer
        [id, positionX, positionY, AR, CA, pseudo, orientation ]
        id : id of the peer
        """
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        controlEvent = factory.createGETPEERINFO(id)
        self.incoming.put(controlEvent)
        return self.ok

    def getAllPeers(self):
        # TODO : return a struct of PEERINFO
        raise NotImplemented()

    def connect(self):
        """ Connect to solipsis. """
        raise NotImplemented()


    def disconnect(self):
        """ Disconnect node
        Return OK """
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        controlEvent = factory.createDISCONNECT
        self.incoming.put(controlEvent)

        return self.ok

    def isAlive(self):
        """ Reply to ping sent by the navigator. """
        return self.ok

    def kill(self):
        """ Kill the node and stop connection betwwen navigator and node
        """
        # send a KILL order to the node
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        kill = factory.createKILL()
        self.incoming.put(kill)

        # stop this connector
        self.connector.stop()

        return self.ok

    def move(self, x, y, z):
        """ Reception of a move order
        x,y,z : target coordinates. These parameters are passed as string
        to avoid int overflow problems
        """
        assert( z == 0)
        pos = Position(long(x), long(y), long(z))
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        move = factory.createMOVE(pos)
        self.incoming.put(move)
        return self.ok

    def set(self, name, value):
        """ Reception of a SET order. Modification of a characteristic of the
        node. E.g. the pseudo set('Pseudo', 'john')"""
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        set = factory.createSET(name, value)
        self.incoming.put(set)
        return self.ok

