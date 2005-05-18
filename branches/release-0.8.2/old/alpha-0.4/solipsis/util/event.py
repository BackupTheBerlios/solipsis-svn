class Event:
    """ Events are used for thread communications. Connectors and node objects
    communicate by sending events.
    Events have a type: 'peer' for communication with peers, 'control' for
    communication with a controller and internal for events fired by the node itself
    Events have a method: which corresponds to the order given through this event.
    E.g. the 'HELLO' method is used to initialize a connection with a remote peer.
    Events have arguments: additionnal information 
    """
    # Possible type of events
    PEER = "peer"
    CONTROL = "control"
    INTERNAL = "internal"

    def createEvent(type, method):
        """ Create a new event. Static method
        type : type of event created, either 'peer', 'control' or 'internal'
        method: method invoked through this event
        Return : a new event object
        Raises: SolipsisInternalError if type is unknown
        """
        event = None
        if type == Event.PEER:
            event = PeerEvent(method)
        elif type == Event.CONTROL:
            event = ControlEvent(method)
        elif type == Event.INTERNAL:
            event = InternalEvent(method)
        else:
            raise SolipsisInternalError('Unknown event type ' + type)

        return event
    
    createEvent = staticmethod(createEvent)
    
    def __init__(self, type, data):
        
        self._type = type
        # raw data for the event
        # E.g 'HEARTBEAT;10.193.161.35:33363'
        self._data = data

        # name of the event, extracted by the parse method 
        self._method = ""
        
        # arguments of this event. It is a hash table {argName -> argValue}
        self._args = {}

        # a string representing the address of the sender of the event
        # E.g. "IP:Port" like "192.165.56.4:1245"
        
        self._senderAddress    = ""
        self._recipientAddress = ""
        
    def getMethod(self):
        return self._method

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

    def setMethod(self, method):
        self._method = method

    def setType(self, type):
        self._type = type

class PeerEvent(Event):

    def __init__(self, data):
        """ Create a new networkEvent object.
        The sender and the recipient fields are NOT set
        type : type of message, 'peer' or 'control'
        data : a raw message, e.g. 'HEARTBEAT;10.193.161.35:33363'
        Raise : a ValueError exception is the message syntax is incorrect
        """
        Event.__init__(self, Event.PEER, data)

        # An exception can be raised here if the syntax of the data is incorrect
        self.msg = Message(data)
            
        # information on who sent this network event
        self.sender_host = ""
        self.sender_port = ""
        self.recipient_host = ""
        self.recipient_port = ""
        
    def setSender(self, sender):
        self.sender_host = sender[0]
        self.sender_port = sender[1]
        address = self.sender_host + ":" + str(self.sender_port)
        self._senderAddress = address
        
    def setRecipient(self, recipient):
        self.recipient_host = recipient[0]
        self.recipient_port = recipient[1]
        address = self.recipient_host + ":" + str(self.recipient_port)
        self._recipientAddress = address
        
    def sender(self):
        return [self.sender_host, int(self.sender_port)]

    def recipient(self):
        return [self.recipient_host, int(self.recipient_port)]
    
    def getMethod(self):
        return self.msg.getMethod()

    def enumerateArgs(self):
        return self.msg.headers.items()

    
class ControlEvent(Event):
    def __init__(self, data):
        Event.__init__(self, Event.CONTROL, data)

class InternalEvent(Event):
    def __init__(self, data):
        Event.__init__(self, Event.INTERNAL, data)
        
class UnknownMessage(Exception):
     def __init__(self):
         pass
    

        
