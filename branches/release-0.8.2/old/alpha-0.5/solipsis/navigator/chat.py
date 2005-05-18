from solipsis.navigator.service import Service
from solipsis.util.exception import SolipsisException

class DuplicateChatterId(SolipsisException):
    pass

class Chat(Service):
    def __init__(self, connectionInfo):
        Service.__init__(self, Service.ID_CHAT,
                         'basic chat service', connectionInfo)
        self.chatters = {}
        self.connector = UDPConnector(Connector.SERVICE, self.events, self.logger,
                                      connectionInfo)
        
    def enumerateChatters(self):
        return self.chatters.values()

    def addChatter(self, chatter):
        id = chatter.getId()
        if not self.chatters.has_key(id):
            self.chatters[id] = chatter
        else:
            raise DuplicateChatterId()
        
    def removeChatter(self, chatter):
        del self.chatters(chatter.getId())

    def getChatter(self, id):
        return self.chatters[id]
    
    def broadcast(self, msg):
        """ Send a message to all chatters """
        for chatter in self.enumerateChatters():
            self.send(chatter.getId(), msg)

    def send(self, chatterId, msg):
        """ Send a message to a chatter """
        cnx = self.getChatter(chatterId).getConnectionInfo()
        self.socket.sendto(msg, cnx)
        
    def run(self):
        while not self.stopping:
            readsock, writesock, errsock = select.select([self.socket], [], [],0)

            if len(readsock):
                try:
                    # receive and process message from other nodes        
                    data, sender = self.socket.recvfrom(self.BUFFER_SIZE)
                    
class Chatter:
    def __init__(self, id, pseudo, connectionInfo):
        self.id = id
        self.pseudo = pseudo
        self.connectionInfo = connectionInfo

    def getId(self):
        return self.id

    def getPseudo(self):
        return self.pseudo

    def getConnectionInfo(self):
        return self.connectionInfo
