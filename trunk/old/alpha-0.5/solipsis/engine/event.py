import re

from solipsis.engine.entity import Entity, Address, Position
from solipsis.util.exception import SolipsisInternalError, SolipsisEventParsingError

class Event:
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

        # a string representing the address of the sender of the event
        # E.g. "IP:Port" like "192.165.56.4:1245"        
        self._senderAddress    = ""
        self._recipientAddress = ""

        # Connector object used to send this event
        self.connector = None
        
    def getRequest(self):
        return self._request

    def enumerateArgs(self):
        return self._args.items()
    
    def getType(self):
        return self._type

    def getData(self):
        return self._data

    def senderAddress(self):
        return self._senderAddress

    def recipientAddress(self):
        return self._recipientAddress

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
        
class ControlEvent(Event):
    def __init__(self, request):
        Event.__init__(self, request)
        self.setType('control')

class InternalEvent(Event):
    def __init__(self, request):
        Event.__init__(self, request)
        self.setType('internal')

        
class PeerEvent(Event):
    
    def __init__(self, request):
        """ Create a new networkEvent object.
        The sender and the recipient fields are NOT set
        type : type of message, 'peer' or 'control'
        data : a raw message, e.g. 'HEARTBEAT;10.193.161.35:33363'
        Raise : a ValueError exception is the message syntax is incorrect
        """
        Event.__init__(self, request)
                    
        # information on who sent this network event
        self.senderAddress = None

        # network address of the recipient of this event
        self.recipientAddress = None
        
    def setSenderAddress(self, address):
        self.senderAddress = address
        
    def setRecipientAddress(self, address):
        self.recipientAddress = address
        
    def getSenderAddress(self):
        return self.senderAddress 

    def getRecipientAddress(self):
        return self.recipientAddress
    
    
class EventFactory:
    """ Class used for creating Solipsis events.
    Peer :best, service, endservice, connect, hello, close, update, heartbeat
    around, queryaround, detect, search, found, findnearest, nearest
    Control : jump, kill
    internal : timer
    """

    theFactory = None
    
    def __init__(self, node):
        """ Internal method, this class should only be called by the init method
        Constructor: create a Event factory object.
        node: the node which creates message through this factory
        """
        if EventFactory.theFactory is not None:
            raise SolipsisInternalError("Error: Event factory object should only be " +
                                        "accessed through the getInstance method"  )
        self.node = node
        self.type = None
    
    def getInstance():
        """ Static method.
        Return the event factory object. The same object is returned even if
        this method is called multiple times
        Raises: SolipsisInternalError if factory class is not initialized
        before using  this method (EventFactory.init must first be called)"""
        if EventFactory.theFactory is not None:
            return  EventFactory.theFactory
        else:
            errormsg = 'Error: trying to use a non initialialized message factory. '
            errormsg = errormsg + 'EventFactory.init(node) must be called first'
            raise SolipsisInternalError(errormsg)

    def init(node):
        """ Static method
        Initilization of the factory, this method must be called before using the
        factory
        """
        if EventFactory.theFactory is None:
            EventFactory.theFactory = EventFactory(node)

        init = staticmethod(init)
        getInstance = staticmethod(getInstance)

    def _addRemoteEntityInfosArgs(self, evt, peer):
        """ Internal method.
        Add all the entity infos args of a peer to a message:
        'Remote-Address', 'Remote-Id', 'Remote-Position',
        'Remote-AwarnessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
        evt : the message to modify
        peer : The peer object used to fill-in the args
        """    
        evt.addArg('Remote-Address', peer.getAddress())
        evt.addArg('Remote-Id', peer.getId())
        evt.addArg('Remote-Position', peer.getStringPosition())
        evt.addArg('Remote-AwarnessRadius', peer.getAwarenessRadius())
        evt.addArg('Remote-Calibre', peer.getCalibre())
        evt.addArg('Remote-Orientation', peer.getOrientation())
        evt.addArg('Remote-Pseudo', peer.getPseudo())

    def _addEntityInfosArgs(self, evt):
        """ Internal method.
        Add all the entity infos args to a message: 'Address', 'Id', 'Position',
        'AwarnessRadius', 'Calibre', 'Orientation', 'Pseudo'
        evt : the message to modify
        """    
        evt.addArg('Address', self.node.getAddress())
        evt.addArg('Id', self.node.getId())
        evt.addArg('Position', self.node.getStringPosition())
        evt.addArg('AwarnessRadius', self.node.getAwarenessRadius())
        evt.addArg('Calibre', self.node.getCalibre())
        evt.addArg('Orientation', self.node.getOrientation())
        evt.addArg('Pseudo', self.node.getPseudo())
       
    def createBestEvt(self):
        """ Create a BEST message. This is the reply to a FINDNEAREST message.
        I'm the closest node to a target position send all  my characteristics:
        Args: 'Address', 'Id', 'Position','AwarnessRadius', 'Calibre',
        'Orientation', 'Pseudo'
        """
        evt = PeerEvent('BEST')
        self._addEntityInfosArgs(evt)
        return evt

    def createConnectEvt(self):
        """ Create a CONNECT message. This is the reply to a HELLO message.
        Connect to a new peer. Send peer  all my characteristics.
        Args: 'Address', 'Id', 'Position','AwarnessRadius', 'Calibre',
        'Orientation', 'Pseudo'
        """
        evt = PeerEvent('CONNECT')
        self._addEntityInfosArgs(evt)
        return evt

    def createHelloEvt(self):
        """ Create a HELLO message. Propose a connection to a new peer. Send peer  all
        my characteristics.
        Args: 'Address', 'Id', 'Position','AwarnessRadius', 'Calibre',
        'Orientation', 'Pseudo'
        """
        evt = PeerEvent('HELLO')
        self._addEntityInfosArgs(evt)
        return evt

    def createFindnearestEvt(self, targetPosition=None):
        """ Create a FINDNEAREST message. We are looking for the peer that is the
        closest to a target postion.
        Args: 'Position'
        targetPosition : optional - a Position object 
        """
        evt = PeerEvent('FINDNEAREST')
        if targetPosition is None:
            evt.addArg('Position', self.node.getStringPosition())
        else:
            evt.addArg('Position', targetPosition.toString())
        return evt

    def createServiceEvt(self, serviceId):
        """ Create a SERVICE message. Send peer a description of the services available
        for this node.
        Args: 'Id', 'ServiceId', 'ServiceDesc', 'ServiceAddress'
        """
        evt = PeerEvent('SERVICE')
        srv = self.node.service[service_id]
        evt.addArg('Id', self.node.id)
        evt.addArg('ServiceId', serviceId)
        evt.addArg('ServiceDesc', srv.desc)
        evt.addArg('ServiceAddress', srv.address)
        return evt

    def createEndserviceEvt(self, serviceId):
        """ Create and ENDSERVICE message. This message is used to notify peers that
        a  service is no longer available.
        serviceIdc : the id of the service that is no longer available."""
        evt = PeerEvent('ENDSERVICE')
        evt.addArg('Id', self.node.id)
        evt.addArg('ServiceId', serviceId)
        return evt

    def createCloseEvt(self):
        """ Create a CLOSE message. Close connection with a peer.
        Args: 'Id'
        """
        evt = PeerEvent('CLOSE')
        evt.addArg('Id', self.node.id)
        return evt

    def createUpdateEvt(self):
        """ Event used to notify peers that one of our characteristics has changed
        name: name of the fied that changed. 'POS' or 'PSEUDO' or 'AR' or 'ORI' or
        'CAL' or 'PSEUDO'
        Args : 'id' and ( 'Position' or 'Orientation' or 'AwarnessRadius' or
        'Calibre' or 'Pseudo' )
        """
        evt = PeerEvent('UPDATE')
        self._addEntityInfosArgs(evt)
        """
        evt.addArg('Id', self.node.getId())
        if ( name == "POS" ):      
          evt.addArg('Position', self.node.getStringPosition())
        elif ( name == "ORI" ):
          evt.addArg('Orientation', self.node.getOrientation())
        elif ( name == "AR"):
          evt.addArg('AwarnessRadius', self.node.getAwarenessRadius())
        elif ( name == "CAL"):
          evt.addArg('Calibre', self.node.getCalibre())
        elif ( name == "PSEUDO"):
          evt.addArg('Pseudo', self.node.getPseudo())
        else:
          raise SolpsisInternalError('Error: unknown field name: '+ name)
        """
        return evt

    def createHeartbeatEvt(self):
        """Create a  HEARTBEAT message. Used to notify peers that we are still alive
        Args: 'Id'    
        """
        evt = PeerEvent('HEARTBEAT')
        evt.addArg('Id', self.node.getId())
        return evt

    def createDetectEvt(self, peer):
        """Create a DETECT message. Used to notify a neighbour that we have detected
        a peer moving toward this neighbour.
        Send info about this peer.
        Args: 'Remote-Address', 'Remote-Id', 'Remote-Position',
        'Remote-AwarnessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
        """ 
        evt = PeerEvent('DETECT')
        self._addRemoteEntityInfosArgs(evt, peer)
        return evt

    def createFoundEvt(self, peer):
        """ Create a FOUND message. This is the reply to a SEARCH message. We found a
        peer that could satisfy the SEARCH criteria. Send information on this remote
        peer.
        Args: 'Remote-Address', 'Remote-Id', 'Remote-Position',
        'Remote-AwarnessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
        """ 
        evt = PeerEvent('FOUND')
        self._addRemoteEntityInfosArgs(evt, peer)
        return evt

    def createSearchEvt(self, isClockwise):
        """ Create a SEARCH message. We need to search a new neighbour because our
        global connectivity rule isn't respected.
        isClockwise : if true search in clockwise direction
        Args: 'Id', 'Clockwise'
        """
        evt = PeerEvent('SEARCH')
        evt.addArg('Id', self.node.getId())
        evt.addArg('Clockwise', isCounterclockwise)
        return evt

    def createQueryaroundEvt(self, idBest, distBest):
        """ Create a QUERYAROUND message. We around looking for all the peers that are
        located around a target position.
        idBest: Id of the peer that is the closest to target position
        distBest: distance of the best peer to target position
        Args: 'Position', 'Best-Id', Best-Distance'
        """
        evt = PeerEvent('QUERYAROUND')
        evt.addArg('Position', self.node.getStringPosition())
        evt.addArg('Best-Id', idBest)
        evt.addArg('Best-Distance',str(distBest))
        return evt

    def createNearestEvt(self, peer):
        """ Create a NEAREST message
        This is the reply to a FINDNEAREST message. Send information on the peer that
        is the nearest to a target position.
        Args: 'Remote-Address', 'Remote-Position'
        """
        evt = PeerEvent('NEAREST')
        evt.addArg('Remote-Address', peer.getAddress())
        evt.addArg('Remote-Position', peer.getStringPosition())
        return evt

    def createAroundEvt(self, peer):
        """ Create a AROUND message. This the reply to a QUERYAROUND message.
        Send information on a peer that is around a target position.
        Args: 'Remote-Address', 'Remote-Id', 'Remote-Position',
        'Remote-AwarnessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
        """
        evt = PeerEvent('AROUND')
        self._addRemoteEntityInfosArgs(evt, peer)
        return evt

    def createJumpEvt(self, position):
        evt = ControlEvent('JUMP')
        evt.addArg('Position', position.toString())
        return evt

    def createNewEvt(self, peer):
        evt = ControlEvent('NEW')
        self._addEntityInfosArgs(self, evt)
        return evt
    
class EventParser:
    VERSION = "SOLIPSIS/1.0"

    ALL_NODE_ARGS = ['Address', 'Id', 'Position', 'AwarnessRadius', 'Calibre',
                     'Orientation', 'Pseudo']
    
    ALL_REMOTE_ARGS = [  'Remote-Address', 'Remote-Id', 'Remote-Position',
                         'Remote-AwarnessRadius', 'Remote-Calibre',
                         'Remote-Orientation', 'Remote-Pseudo']
    
    REQUESTS = {
        'AROUND'     : ALL_REMOTE_ARGS,
        'BEST'       : ALL_NODE_ARGS,
        'CLOSE'      : ['Id'],
        'CONNECT'    : ALL_NODE_ARGS,
        'DETECT'     : ALL_REMOTE_ARGS,
        'ENDSERVICE' : ['Id', 'ServiceId'],
        'FINDNEAREST': ['Position'],
        'FOUND'      : ALL_REMOTE_ARGS,
        'HEARTBEAT'  : ['Id'],
        'HELLO'      : ALL_NODE_ARGS,
        'NEAREST'    : ['Remote-Address', 'Remote-Position'],      
        'QUERYAROUND': ['Position', 'Best-Id', 'Best-Distance'],
        'SEARCH'     : ['Id', 'Clockwise'],
        'SERVICE'    : ['Id', 'ServiceId', 'ServiceDesc', 'ServiceAddress'],
        'UPDATE'     : ALL_NODE_ARGS    
        }
  
    ARGS_SYNTAX = {    
        'Address'       :  '\s*.*:\d+\s*',
        'AwarnessRadius': '\d+',
        'Calibre'       : '\d{1,4}',
        'Distance'      : '\d+',
        'Id'            : '.*',
        'Orientation'   : '\d{1,3}',
        'Position'      : '^\s*\d+\s*-\s*\d+$',
        'Pseudo'        : '.*'
        }
    
    ARGS_SYNTAX['Best-Id']               = ARGS_SYNTAX['Id']
    ARGS_SYNTAX['Best-Distance']         = ARGS_SYNTAX['Distance']
    ARGS_SYNTAX['Remote-Address']        = ARGS_SYNTAX['Address']
    ARGS_SYNTAX['Remote-AwarnessRadius'] = ARGS_SYNTAX['AwarnessRadius']
    ARGS_SYNTAX['Remote-Calibre']        = ARGS_SYNTAX['Calibre']
    ARGS_SYNTAX['Remote-Distance']       = ARGS_SYNTAX['Distance']
    ARGS_SYNTAX['Remote-Id']             = ARGS_SYNTAX['Id']
    ARGS_SYNTAX['Remote-Orientation']    = ARGS_SYNTAX['Orientation']
    ARGS_SYNTAX['Remote-Position']       = ARGS_SYNTAX['Position']
    ARGS_SYNTAX['Remote-Pseudo']         = ARGS_SYNTAX['Pseudo']

    def __init__(self, event=None):
        if event is not None:
            self.request = event.getRequest()
            self.args = event.getAllArgs()
        else:
           self.request = ""
           self.args = {}
           
    def createEvent(self, rawData):
        """ Parse a message sent by a peer and create the corresponding event.
        rawData: a string representing a message
        Return : an event object
        Raises: SolipsisEventParsingException if the syntax of the message
        is incorrect
        """
        self.request = ""
        self.args = {}

        # create an empty message
        if rawData == "":
          self._data = ""      
        else:
          self._data = rawData
          # parse raw data to construct message
          data = rawData.splitlines()
          requestLinePattern = re.compile('(\w+)\s+(SOLIPSIS/\d+\.\d+)')
          requestLineMatch = requestLinePattern.match(data[0])
          if requestLineMatch is None:
            raise SolipsisEventParsingError("Invalid message syntax")

          # Request is first word of the first line (e.g. NEAREST, or BEST ...)
          request = requestLineMatch.group(1).upper()
          # extract protocol version
          version = requestLineMatch.group(2).upper()

          if not EventParser.REQUESTS.has_key(request):        
            raise SolipsisEventParsingError("Unknown request:" + request)

          self.request = request

          # Get args for this request
          argList = EventParser.REQUESTS[request]

          # We are looking for
          # * a word that can contain a '-' like Address or Remote-Address:
          #   (\w+(?:-\w+)?)  --> (?:) is used for non capturing groups, because we
          #                       don't want to catch '-Address' as a group 
          # * followed by a ':' : \s*:\s*
          # * and followed by anything - the arg value : (.*) 
          argPattern = re.compile(r'(\w+(?:-\w+)?)\s*:\s*(.*)')

          # Parse all args included in message and check their syntax
          for line in data[1:]:        
            argMatch = argPattern.match(line)
            if argMatch is None:
              raise SolipsisEventParsingError("Invalid message syntax")

            # Get arg name and arg value
            argName = argMatch.group(1)
            argVal = argMatch.group(2)

            if argName not in argList:
              raise SolipsisEventParsingError("Unknown arg " + argName +
                                                " for message " + request)


            # check the syntax of the arg (e.g. for a calibre we expect a 3 digits
            # number)
            if EventParser.ARGS_SYNTAX.has_key(argName):
              # syntax of each arg is stored in ARGS_SYNTAX hash table
              argSyntax = re.compile(EventParser.ARGS_SYNTAX[argName])
              if argSyntax.match(argVal) is not None:
                # the syntax is correct add this arg to the EventParser object
                self.addArg(argName, argVal)
              else:
                raise SolipsisEventParsingError("Invalid arg '" + argName +
                                                  "' syntax:" + argVal)          
            else:
              # we have an unknown arg, if solipsis version is different just
              # skip this arg, else raise an error
              if version == EventParser.VERSION:
                raise SolipsisEventParsingError(EventParser.VERSION + "Unknown arg " +
                                                  argName + " in message " + request)

          # We have added all the args we need to check now 
          # that all args where added to the message
          if len(self.args) < len(argList):
            # some args are missing
            raise SolipsisEventParsingError("Missing args in message " + request)
          elif len(self.args) > len(argList):
            # we have added too many args, it means that we have duplicate args
            raise SolipsisEventParsingError("Duplicate arg in message "+ request)

        # create a new event based on the parsed information
        newEvent = Event(self.request)
        newEvent.setAllArgs(self.args)

        return newEvent

    def addArg(self, argName, argValue):
        self.args[argName] = argValue
        
    def setRequest(self, value):
        self.request = value

    def data(self):
        buffer = self.request + " " + EventParser.VERSION + "\r\n"
        for (k,v) in self.args.items():
          line =  '%s: %s\r\n' % (k, str(v))
          buffer = buffer + line
        return buffer
    
    def __repr__(self):
        """ String representation of the message """
        return self.data()

    def createEntity(self):
        """ Parse the event and return an Entity object initilized with information
        included in the event
        Return : a new Entity object
        """
        ent = Entity()
        if self.args.has_key('Id'):
            ent.setId(self.args['Id'])

        if self.args.has_key('Address'):
            ent.setAddress(self.args['Address'])
            
        if self.args.has_key('Position'):
            ent.setPosition(self.args['Position'])

        if self.args.has_key('Orientation'):
            ent.setOrientation(self.args['Orientation'])

        if self.args.has_key('AwarnessRadius'):
            ent.setAwarnessRadius(self.args['AwarnessRadius'])

        if self.args.has_key('Calibre'):
            ent.setCalibre(self.args['Calibre'])

        if self.args.has_key('Pseudo'):
            ent.setPseudo(self.args['Pseudo'])

        return ent
