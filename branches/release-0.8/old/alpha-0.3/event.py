class Event:
    def __init__(self, type, data):
        
        self._type = type
        # raw data for the event
        # E.g 'HEARTBEAT;10.193.161.35:33363'
        self._data = data

        # name of the event, extracted by the parse method 
        self._name = ""
        # arguments extracted by the parse method
        self._args = ""

        # a string representing the address of the sender of the event
        # E.g. "IP:Port" like "192.165.56.4:1245"
        
        self._senderAddress    = ""
        self._recipientAddress = ""
        
    def name(self):
        return self._name

    def args(self):
        return self._args
    
    def type(self):
        return self._type

    def data(self):
        return self._data

    def senderAddress(self):
        return self._senderAddress

    def recipientAddress(self):
        return self._recipientAddress

    def setName(self, name):
        self._name = name

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
        Event.__init__(self, "peer", data)

        # parse the message
        self.parse()
        
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
    
    def parse(self):
        """ parse the message associated with this network event. Message name
        and arguments are extracted
        Return : none
        Raise : ValueError when message syntax is oncorrect
        """
        # TODO remove this case with next  version of solipsis
        if (self._data == "HI" ):
            self._name = self.data()
            self._args = ""
        else:
            all = self._data.split(";")
            self._name = all[0]            
            self._args = all[1:]

    
    def encodeMsg(self, args):
        """ Encode a solipsis message
        args : list of arguments of the message
        Return: an encoded message
        E.g. : ['HEARTBEAT', '193.23.235.5:2356'] --> 'HEARTBEAT;193.23.235.5:2356'
        """
        return ";".join(args)
        


        
class ControlEvent(Event):
    def __init__(self, data):
        Event.__init__(self, "control", data)
        
class UnknownMessage(Exception):
     def __init__(self):
         pass
    
