from event import Event, EventFactory, EventParser
from peer import Peer
import protocol

class PeerEvent(Event):
    TYPE = 'peer'

    def __init__(self, request):
        Event.__init__(self, request)
        self.setType(PeerEvent.TYPE)
        self._senderAddress    = None
        self._recipientAddress = None

    def setSenderAddress(self, address):
        self._senderAddress = address

    def setRecipientAddress(self, address):
        self._recipientAddress = address

    def getSenderAddress(self):
        return self._senderAddress

    def getRecipientAddress(self):
        return self._recipientAddress

    def __str__(self):
        return PeerEventParser().getData(self)

    def createPeer(self):
        """ Parse the event and create the Peer object associated with this event"""
        return Peer(id = self.getArg(protocol.ARG_ID),
                    address = self.getArg(protocol.ARG_ADDRESS),
                    position = self.getArg(protocol.ARG_POSITION),
                    awarenessRadius = self.getArg(protocol.ARG_AWARENESS_RADIUS),
                    calibre = self.getArg(protocol.ARG_CALIBRE),
                    orientation = self.getArg(protocol.ARG_ORIENTATION),
                    pseudo = self.getArg(protocol.ARG_PSEUDO))

    def createRemotePeer(self):
        """ Parse the event and create the Peer object associated with this event

        The vent is composed of REMOTE fields
        """
        return Peer(id = self.getArg(protocol.ARG_REMOTE_ID),
                    address = self.getArg(protocol.ARG_REMOTE_ADDRESS),
                    position = self.getArg(protocol.ARG_REMOTE_POSITION),
                    awarenessRadius = self.getArg(protocol.ARG_REMOTE_AWARENESS_RADIUS),
                    calibre = self.getArg(protocol.ARG_REMOTE_CALIBRE),
                    orientation = self.getArg(protocol.ARG_REMOTE_ORIENTATION),
                    pseudo = self.getArg(protocol.ARG_REMOTE_PSEUDO))


class PeerEventParser(EventParser):
    def __init__(self):
        super(PeerEventParser, self).__init__()

    def getData(self, event):
        """
        Build a Solipsis message from an event object.
        """
        message = protocol.Message()
        message.request = event.getRequest()
        for (arg, value) in event.enumerateArgs():
            #message.__setattr__(arg, value)
            message.args[arg] = value
        return message.toData()

    def createEvent(self, rawData):
        """
        Parse a message sent by a peer and create the corresponding event.
        rawData: a string representing a message
        Return : an event object
        Raises: SolipsisEventParsingException if the syntax of the message
        is incorrect
        """
        message = protocol.Message()
        if message.fromData(rawData):
            # If the message is not empty, create a new event based on the parsed information
            newEvent = PeerEvent(message.request)
            newEvent.setAllArgs(message.args)
            return newEvent
        else:
            return None


class PeerEventFactory(EventFactory):
    TYPE = PeerEvent.TYPE

    def createBEST(self):
        """ Create a BEST message. This is the reply to a FINDNEAREST message.
        I'm the closest node to a target position send all  my characteristics:
        Args: 'Address', 'Id', 'Position','AwarenessRadius', 'Calibre',
        'Orientation', 'Pseudo'
        """
        evt = PeerEvent('BEST')
        self._addNodeInfosArgs(evt)
        return evt

    def createCONNECT(self):
        """ Create a CONNECT message. This is the reply to a HELLO message.
        Connect to a new peer. Send peer  all my characteristics.
        Args: 'Address', 'Id', 'Position','AwarenessRadius', 'Calibre',
        'Orientation', 'Pseudo'
        """
        evt = PeerEvent('CONNECT')
        self._addNodeInfosArgs(evt)
        return evt

    def createHELLO(self):
        """ Create a HELLO message. Propose a connection to a new peer. Send peer  all
        my characteristics.
        Args: 'Address', 'Id', 'Position','AwarenessRadius', 'Calibre',
        'Orientation', 'Pseudo'
        """
        evt = PeerEvent('HELLO')
        self._addNodeInfosArgs(evt)
        return evt

    def createFINDNEAREST(self, targetPosition=None):
        """ Create a FINDNEAREST message. We are looking for the peer that is the
        closest to a target postion.
        Args: 'Position'
        targetPosition : optional - a Position object - if not specified use
        the node current position for the target
        """
        evt = PeerEvent('FINDNEAREST')
        if targetPosition is None:
            evt.addArg('Position', self.node.getPosition())
        else:
            evt.addArg('Position', targetPosition)
        return evt

    def createADDSERVICE(self, serviceId):
        """ Create a SERVICE message. Send peer a description of the services available
        for this node.
        Args: 'Id', 'ServiceId', 'ServiceDesc', 'ServiceAddress'
        """
        evt = PeerEvent('SERVICE')
        srv = self.node.service[serviceId]
        evt.addArg(protocol.ARG_ID, self.node.id)
        evt.addArg(protocol.ARG_SERVICE_ID, serviceId)
        evt.addArg(protocol.ARG_SERVICE_DESC, srv.desc)
        evt.addArg(protocol.ARG_SERVICE_ADDRESS, srv.address)
        return evt

    def createDELSERVICE(self, serviceId):
        """ Create and ENDSERVICE message. This message is used to notify peers that
        a  service is no longer available.
        serviceIdc : the id of the service that is no longer available."""
        evt = PeerEvent('ENDSERVICE')
        evt.addArg(protocol.ARG_ID, self.node.id)
        evt.addArg(protocol.ARG_SERVICE_ID, serviceId)
        return evt

    def createCLOSE(self):
        """ Create a CLOSE message. Close connection with a peer.
        Args: 'Id'
        """
        evt = PeerEvent('CLOSE')
        evt.addArg('Id', self.node.id)
        return evt

    def createUPDATE(self):
        """ Event used to notify peers that one of our characteristics has changed
        name: name of the fied that changed. 'POS' or 'PSEUDO' or 'AR' or 'ORI' or
        'CAL' or 'PSEUDO'
        Args : 'id' and ( 'Position' or 'Orientation' or 'AwarenessRadius' or
        'Calibre' or 'Pseudo' )
        """
        evt = PeerEvent('UPDATE')
        self._addNodeInfosArgs(evt)
        """
        evt.addArg('Id', self.node.getId())
        if ( name == "POS" ):
          evt.addArg('Position', self.node.getStringPosition())
        elif ( name == "ORI" ):
          evt.addArg('Orientation', self.node.getOrientation())
        elif ( name == "AR"):
          evt.addArg('AwarenessRadius', self.node.getAwarenessRadius())
        elif ( name == "CAL"):
          evt.addArg('Calibre', self.node.getCalibre())
        elif ( name == "PSEUDO"):
          evt.addArg('Pseudo', self.node.getPseudo())
        else:
          raise SolpsisInternalError('Error: unknown field name: '+ name)
        """
        return evt

    def createHEARTBEAT(self):
        """Create a  HEARTBEAT message. Used to notify peers that we are still alive
        Args: 'Id'
        """
        evt = PeerEvent('HEARTBEAT')
        evt.addArg('Id', self.node.getId())
        return evt

    def createDETECT(self, peer):
        """Create a DETECT message. Used to notify a neighbour that we have detected
        a peer moving toward this neighbour.
        Send info about this peer.
        Args: 'Remote-Address', 'Remote-Id', 'Remote-Position',
        'Remote-AwarenessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
        """
        evt = PeerEvent('DETECT')
        self._addRemoteEntityInfosArgs(evt, peer)
        return evt

    def createFOUND(self, peer):
        """ Create a FOUND message. This is the reply to a SEARCH message. We found a
        peer that could satisfy the SEARCH criteria. Send information on this remote
        peer.
        Args: 'Remote-Address', 'Remote-Id', 'Remote-Position',
        'Remote-AwarenessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
        """
        evt = PeerEvent('FOUND')
        self._addRemoteEntityInfosArgs(evt, peer)
        return evt

    def createSEARCH(self, isClockwise):
        """ Create a SEARCH message. We need to search a new neighbour because our
        global connectivity rule isn't respected.
        isClockwise : if true search in clockwise direction
        Args: 'Id', 'Clockwise'
        """
        evt = PeerEvent('SEARCH')
        evt.addArg(protocol.ARG_ID, self.node.getId())
        evt.addArg(protocol.ARG_CLOCKWISE, isClockwise)
        return evt

    def createQUERYAROUND(self, idBest, distBest):
        """ Create a QUERYAROUND message. We around looking for all the peers that are
        located around a target position.
        idBest: Id of the peer that is the closest to target position
        distBest: distance of the best peer to target position
        Args: 'Position', 'Best-Id', Best-Distance'
        """
        evt = PeerEvent('QUERYAROUND')
        evt.addArg(protocol.ARG_POSITION, self.node.getPosition())
        evt.addArg(protocol.ARG_BEST_ID, idBest)
        evt.addArg(protocol.ARG_BEST_DISTANCE,str(distBest))
        return evt

    def createNEAREST(self, peer):
        """ Create a NEAREST message
        This is the reply to a FINDNEAREST message. Send information on the peer that
        is the nearest to a target position.
        Args: 'Remote-Address', 'Remote-Position'
        """
        evt = PeerEvent('NEAREST')
        evt.addArg(protocol.ARG_REMOTE_ADDRESS, peer.getAddress())
        evt.addArg(protocol.ARG_REMOTE_POSITION, peer.getPosition())
        return evt

    def createAROUND(self, peer):
        """ Create a AROUND message. This the reply to a QUERYAROUND message.
        Send information on a peer that is around a target position.
        Args: 'Remote-Address', 'Remote-Id', 'Remote-Position',
        'Remote-AwarenessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
        """
        evt = PeerEvent('AROUND')
        self._addRemoteEntityInfosArgs(evt, peer)
        return evt



