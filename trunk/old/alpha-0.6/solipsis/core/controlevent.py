from solipsis.core.event import Event, EventParser, EventFactory, Notification
from solipsis.util.exception import EventParsingError


class ControlEvent(Event):
    TYPE = 'control'

    def __init__(self, request):
        super(ControlEvent, self).__init__(request)
        self.setType(ControlEvent.TYPE)

class ControlEventParser(EventParser):
    def getData(self, event):
        return Notification(event)

    def createEvent(self, request, *args, **kargs):
        factory = ControlEventFactory()
        method = getattr(factory, "create" + request)
        #stmt = 'factory.create' + request + '(kargs)'
        try:
            event = method(*args, **kargs)
        except:
            EventParsingError('Unknow control request')
        return event

class ControlEventFactory(EventFactory):
    TYPE = ControlEvent.TYPE

    #
    # These events are created by the node and sent to the navigator
    #
    def createNEW(self, peer):
        """ Notify Navigator that we have connected to a new Peer """
        evt = ControlEvent('NEW')
        evt._addEntityInfosArgs(peer)
        return evt

    def createDEAD(self, peerId):
        """ Notify Navigator that we have disconnected from a Peer"""
        evt = ControlEvent('DEAD')
        evt.addArg('Id', peerId)
        return evt


    def createUPDATE(self, entity):
        """ Notify Navigator that an Entity has changed
        entity : Entity object
        """
        evt = ControlEvent('UPDATE')
        evt._addEntityInfosArgs(entity)
        return evt

    def createNODEINFO(self):
        """ Send our characteristics to the navigator """
        evt = ControlEvent('NODEINFO')
        self._addNodeInfosArgs(evt)
        return evt

    def createERROR(self, message):
        """ An error occured, send an explanation message to the controller
        message : text message explaining the error
        """
        evt = ControlEvent('ERROR')
        evt.addArg('Message', message)
        return evt

    def createABORT(self, message):
        """ A fatal error occurred, the node must destroy itself. """
        evt = ControlEvent('ABORT')
        evt.addArg('Message', message)
        return evt

    def createNEWSERVICE(self, entityId, ServiceId, ServiceDesc,
                              ServiceAddress):
        """ Notify the controller that a peer has a new service."""
        evt = ControlEvent('NEWSERVICE')
        evt.addArg('Id', entityId)
        evt.addArg('ServiceId', ServiceId)
        evt.addArg('ServiceDesc', ServiceDesc)
        evt.addArg('ServiceAddress', ServiceAddress)
        return evt

    def createENDSERVICE(self, entityId, ServiceId):
        """ Notify navigator that the peer with ID entityId no longer has service
        with ID: ServiceId"""
        evt = ControlEvent('ENDSERVICE')
        evt.addArg('Id', entityId)
        evt.addArg('ServiceId', ServiceId)
        return evt


    #
    # These events are created by the navigator and sent to the node
    #
    def createADDSERVICE(self, ServiceId, ServiceDesc, ServiceAddress):
        """ A new service is available in our navigator """
        evt = ControlEvent('ADDSERVICE')
        evt.addArg('ServiceId', ServiceId)
        evt.addArg('ServiceDesc', ServiceDesc)
        evt.addArg('ServiceAddress', ServiceAddress)
        return evt

    def createDELSERVICE(self, ServiceId):
        """ Service with ID ServiceId is no longer available in our navigator"""
        evt = ControlEvent('DELSERVICE')
        evt.addArg('ServiceId', ServiceId)
        return evt

    def createJUMP(self, position):
        """ Jump to traget Position
        position : a Position object
        """
        evt = ControlEvent('JUMP')
        evt.addArg('Position', position)
        return evt

    def createMOVE(self, position):
        """ Jump to traget Position
        position : a Position object
        """
        evt = ControlEvent('MOVE')
        evt.addArg('Position', position.toString())
        return evt

    def createCONNECT(self, controlPort, notificationPort):
        evt = ControlEvent('CONNECT')
        evt.addArg('Control-Port', controlPort)
        evt.addArg('Notification-Port', notificationPort)
        return evt

    def createDISCONNECT(self):
        evt = ControlEvent('DISCONNECT')
        return evt

    def createSET(self, name, value):
        """ Set a characteritic of the node to a new value
        name : name of the field to set, e.g. 'Pseudo'
        value: new value for this field e.g. 'john_smith'
        """
        evt = ControlEvent('SET')
        evt.addArg('Name', name)
        evt.addArg('Value', value)
        return evt

    def createKILL(self):
        evt = ControlEvent('KILL')
        return evt

    def createGETNODEINFO(self):
        """ Send our characteristics to the navigator """
        evt = ControlEvent('GETNODEINFO')
        return evt

    def createGETPEERINFO(self, peerid):
        """ Send the characteristics of a peer to the navigator """
        evt = ControlEvent('GETPEERINFO')
        evt.addArg('Id', peerid)
        return evt

    def createTIMER(self):
        evt = ControlEvent('TIMER')
        return evt
