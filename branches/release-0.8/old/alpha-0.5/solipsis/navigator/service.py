class Service:
    ID_UNKNOWN = 0
    ID_CHAT = 1
    ID_FILE_TRANSFER = 2
    ID_AVATAR = 3

    def __init__(self, id, desc, connectionInfo):
        self.id = id
        self.desc = desc
        self.connectionInfo = connectionInfo
        self.stopping = False
        
    def getId(self):
        return self.id

    def getDescription(self):
        return self.desc

    def getConnectionInfo(self):
        return self.connectionInfo

    def stop(self):
        """ stop the service """
        self.stopping = True
