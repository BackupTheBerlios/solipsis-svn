class Service(object):
    ID_UNKNOWN = 0
    ID_CHAT = 1
    ID_FILE_TRANSFER = 2
    ID_AVATAR = 3

    def __init__(self, id, desc, address):
        """ Constructor.
        id : a string representing the id of the service
        desc : the description of the service
        address: a string describing how to connect to the service
        e.g. '192.168.10.2:8977'
        """
        self.id = id
        self.desc = desc
        self.address = address
        self.isStopping = False
        self.outgoing = NotificationQueue()

    def getId(self):
        return self.id

    def getDescription(self):
        return self.desc

    def getAddress(self):
        return self.address

    def stop(self):
        """ stop the service """
        self.isStopping = True
