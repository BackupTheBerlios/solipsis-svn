from solipsis.util.exception import SolipsisInternalError

class AbstractSubscriber:
    def NEW(self, event):
        """ Abstract method : this method must be implemented by a sub-class
        We have discovered a new Peer.
        event : an Event object containing the peer information
        """
        raise SolipsisAbstractMethodError()

    def NODEINFO(self, event):
        """ Abstract method : this method must be implemented by a sub-class
        
        """
        raise SolipsisAbstractMethodError()

