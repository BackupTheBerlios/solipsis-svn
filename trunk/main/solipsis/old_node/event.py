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
from entity import Entity
from solipsis.util.address import Address
from solipsis.util.geometry import Position
import protocol
import string, re
from exceptions import *

class Event(object):
    """ Events are used for thread communications. Connectors and node objects
    communicate by sending events.
    Events have a request: which corresponds to the order given through this event.
    E.g. the 'HELLO' request is used to initialize a connection with a remote peer.
    Events have arguments: additionnal information
    """

    def __init__(self, request):

        self._request = request

        # arguments of this event. It is a hash table {argName -> argValue}
        self._args = {}

        # Connector object used to send this event
        self._connector = None

    def __str__(self):
        buffer = self.getRequest() + '\r\n'
        for (k,v) in self.enumerateArgs():
            line =  '%s: %s\r\n' % (k, str(v))
            buffer = buffer + line
        return buffer

    def getRequest(self):
        return self._request

    def enumerateArgs(self):
        return self._args.items()

    def getType(self):
        return self._type

    def setRequest(self, request):
        self._request = request

    def setType(self, type):
        self._type = type

    def setAllArgs(self, args):
        self._args = args

    def getAllArgs(self):
        return self._args

    def setConnector(self, connector):
        self._connector = connector

    def getConnector(self):
        return self._connector

    def addArg(self, argName, argValue):
        self._args[argName] = argValue

    def _addEntityInfosArgs(self, entity):
        """ Internal method.
        Add all the entity infos args to an event: 'Address', 'Id', 'Position',
        'AwarenessRadius', 'Calibre', 'Orientation', 'Pseudo'
        entity : an Entity object
        """
        self.addArg(protocol.ARG_ADDRESS, entity.getAddress())
        self.addArg(protocol.ARG_ID, entity.getId())
        self.addArg(protocol.ARG_POSITION, entity.getPosition())
        self.addArg(protocol.ARG_AWARENESS_RADIUS, entity.getAwarenessRadius())
        self.addArg(protocol.ARG_CALIBRE, entity.getCalibre())
        self.addArg(protocol.ARG_ORIENTATION, entity.getOrientation())
        self.addArg(protocol.ARG_PSEUDO, entity.getPseudo())

    def hasArg(self, argName):
        """ Return True if the event has an argument with name = 'argname' """
        return self._args.has_key(argName)

    def getArg(self, argName):
        """ Return the value of argument 'argName'"""
        return self._args[argName]

class InternalEvent(Event):
    def __init__(self, request):
        Event.__init__(self, request)
        self.setType('internal')

class ServiceEvent(Event):
    def __init__(self, request):
        Event.__init__(self, request)
        self.setType('service')

class EventParser(object):
    def getData(self, event):
        raise AbstractMethodError()

    def createEvent(self, *args, **kargs):
        raise AbstractMethodError()

    def createEntity(self, event):
        """ Parse the event and return an Entity object initilized with information
        included in the event
        Return : a new Entity object
        """
        ent = Entity()
        if event.hasArg(protocol.ARG_ID):
            ent.setId(event.getArg(protocol.ARG_ID))

        if event.hasArg(protocol.ARG_ADDRESS):
            ent.setAddress(event.getArg(protocol.ARG_ADDRESS))

        if event.hasArg(protocol.ARG_POSITION):
            ent.setPosition(event.getArg(protocol.ARG_POSITION))

        if event.hasArg(protocol.ARG_ORIENTATION):
            ent.setOrientation(event.getArg(protocol.ARG_ORIENTATION))

        if event.hasArg(protocol.ARG_AWARENESS_RADIUS):
            ent.setAwarenessRadius(event.getArg(protocol.ARG_AWARENESS_RADIUS))

        if event.hasArg(protocol.ARG_CALIBRE):
            ent.setCalibre(event.getArg(protocol.ARG_CALIBRE))

        if event.hasArg(protocol.ARG_PSEUDO):
            ent.setPseudo(event.getArg(protocol.ARG_PSEUDO))

        return ent


class EventFactory(object):
    """ Class used for creating Solipsis events.
    Peer :best, service, endservice, connect, hello, close, update, heartbeat
    around, queryaround, detect, search, found, findnearest, nearest
    Control : jump, kill
    internal : timer
    """

    factories = {}
    node = None

    def getInstance(factoryType):
        """ Static method.
        Return the event factory object. The same object is returned even if
        this method is called multiple times
        Raises: SolipsisInternalError if factory class is not initialized
        before using  this method (EventFactory.init must first be called)"""
        return EventFactory.factories[factoryType]

    def init(node):
        """ Static method
        Initilization of the factory, this method must be called before using the
        factory
        """
        EventFactory.node = node

    def register(factoryType, factory):
        EventFactory.factories[factoryType] = factory
        factory.setNode(EventFactory.node)

    def setNode(self, node):
        self.node = node

    def _addRemoteEntityInfosArgs(self, evt, peer):
        """ Internal method.
        Add all the entity infos args of a peer to a message:
        'Remote-Address', 'Remote-Id', 'Remote-Position',
        'Remote-AwarenessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
        evt : the message to modify
        peer : The peer object used to fill-in the args
        """
        evt.addArg(protocol.ARG_REMOTE_ADDRESS, peer.getAddress())
        evt.addArg(protocol.ARG_REMOTE_ID, peer.getId())
        evt.addArg(protocol.ARG_REMOTE_POSITION, peer.getPosition())
        evt.addArg(protocol.ARG_REMOTE_AWARENESS_RADIUS, peer.getAwarenessRadius())
        evt.addArg(protocol.ARG_REMOTE_CALIBRE, peer.getCalibre())
        evt.addArg(protocol.ARG_REMOTE_ORIENTATION, peer.getOrientation())
        evt.addArg(protocol.ARG_REMOTE_PSEUDO, peer.getPseudo())

    def _addNodeInfosArgs(self, evt):
        """ Internal method.
        Add all the entity infos args to a message: 'Address', 'Id', 'Position',
        'AwarenessRadius', 'Calibre', 'Orientation', 'Pseudo'
        evt : the message to modify
        """
        evt.addArg(protocol.ARG_ADDRESS, self.node.getAddress())
        evt.addArg(protocol.ARG_ID, self.node.getId())
        evt.addArg(protocol.ARG_POSITION, self.node.getPosition())
        evt.addArg(protocol.ARG_AWARENESS_RADIUS, self.node.getAwarenessRadius())
        evt.addArg(protocol.ARG_CALIBRE, self.node.getCalibre())
        evt.addArg(protocol.ARG_ORIENTATION, self.node.getOrientation())
        evt.addArg(protocol.ARG_PSEUDO, self.node.getPseudo())

    init = staticmethod(init)
    getInstance = staticmethod(getInstance)
    register = staticmethod(register)


class Notification:
    """ This is a container class used to send notifications to a navigator """
    def __init__(self, event=None, request='', id = '', position = '', pseudo = '',
                 orientation = '', calibre = 0, address = '', awarenessRadius = '',
                 serviceId = '',serviceDesc = '' ,serviceAddress = ''):
        """ Create a Notification"""
        if event is not None:
            self.setFro