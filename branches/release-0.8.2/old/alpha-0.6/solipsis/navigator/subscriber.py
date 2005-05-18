from solipsis.util.exception import AbstractMethodError

class AbstractSubscriber(object):
    """ The AbstractSubscriber presents the interface that should be implemented by
    classes who want to be notified of events coming from the Node."""
    def NEW(self, peer):
        """ Abstract method : this method must be implemented by a sub-class
        We have discovered a new Peer.
        peer : a Peer Object
        """
        raise AbstractMethodError()

    def NODEINFO(self, node):
        """ Abstract method : this method must be implemented by a sub-class

        nodeinfo: a NodeInfo object
        """
        raise AbstractMethodError()

    def UPDATE(self, entityId, entityFieldName, newFieldValue):
        """ Abstract method : this method must be implemented by a sub-class

        'entityId' : Id of the entity to update
        'entityFieldName' : what is the characteristic to update
        'newFieldValue' : the new value
        """
        raise AbstractMethodError()

    def OnNodeCreationFailure(self, reason):
        """ Abstract method : this method must be implemented by a sub-class
        Failure of the node creation operation
        reason : reason why the node couldn' be created
        """
        raise AbstractMethodError()

    def OnNodeCreationSuccess(self):
        """ Abstract method : this method must be implemented by a sub-class
        The node was successfully created """
        raise AbstractMethodError()
