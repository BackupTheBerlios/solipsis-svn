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
            self.setFromEvent(event)
        else:
            self.request = request
            self.id = id
            self.position = position
            self.pseudo = pseudo
            self.orientation = orientation
            self.calibre = calibre
            self.address = address
            self.awarenessRadius = awarenessRadius
            self.serviceId = serviceId
            self.serviceDesc = serviceDesc
            self.serviceAddress = serviceAddress

    def setFromEntity(self, entity):
        """ Fill-in this Notification using an Entity object"""
        self.id = entity.getId()
        self.pseudo = entity.getPseudo()
        self.orientation = entity.getOrientation()
        self.calibre = entity.getCalibre()
        self.awarenessRadius= str(entity.getAwarenessRadius())
        self.position = entity.getPosition().toString()
        self.address = entity.getAddress.toString()

    def setFromService(self, service):
        """ Fill-in this Notification using a Service object"""
        self.serviceId = service.getId()
        self.serviceDesc = service.getDescription()
        self.serviceAddress = service.getAddress().toString()

    def setFromEvent(self, event):
        self.request = event.getRequest()
        for (k,v) in event.enumerateArgs():
            # convert fields names to their equivalent
            # e.g. Awareness-Radius --> awarnessRadius
            fieldList = k.lower().split('-')
            field = fieldList[0]
            if len(fieldList) > 1:
                field = field + string.join(map(string.capitalize, fieldList[1:]))
            if field == 'position' or field == 'address' or \
                   field == 'serviceAddress' or field == 'awarenessRadius':
                self.__dict__[field] = str(v)
            else:
                self.__dict__[field] = v

    def createEvent(self):
        """ Create the Event object corresponding to this Notification"""
        evt = Event(self.request)
        for (k,v) in self.__dict__.items():
            if k <> 'request':
                pattern = re.compile(r'^([a-z]+)([A-Z][a-z]+)*')
                match = pattern.match(k)
                list = []
                for part in match.groups():
                    if part is not None:
                        list.append(string.capitalize(part))
                #list = map(string.capitalize, match.groups())
                name = list[0]
                value = v
                if len(list) > 1:
                    name = '-'.join(list)
                if name == 'Position':
                    value = Position()
                    value.setValueFromString(v)
                elif name == 'Address' or name == 'Service-Address':
                    value = Address()
                    value.setValueFromString(v)
                elif name == 'Awareness-Radius':
                    value = long(v)

                evt.addArg(name,value)

        return evt


    def __str__(self):
        buff = ""
        for (k,v) in self.__dict__.items():
            buff += '%s -> %s\n' %(k, v)
        return buff
