class State:
    def __init__(self, node, logger):
        self.node = node
        self.logger = logger
    

    def FINDNEAREST(self, event): pass
    

class NotConnected(State):
    """ Intial state of the node. We are not connected to any entity"""

    def JUMP(self, jumpEvent):
        """
        JUMP control event. Move this node to a target position.
        jumpEvent : Request = JUMP, args = {'Position'}
        """
        manager = self.node.getPeersManager()
        peer = manager.getRandomPeer()

        newStrPosition = jumpEvent.getArg('Position')
        newPosition = Position()
        newPosition.setValueFromString(newStrPosition)

        self.node.setPosition(newPosition)
        
        # create a find nearest event
        factory = EventFactory.getInstance()
        findnearest = factory.createFindnearestEvt(newPosition)
        findnearest.setRecipientAddress(peer.getAddress())
        
        self.node.fire(findnearest)
        self.node.setState('Connecting')
        # TODO : how to implement retry ?
        # using a timer, or by sending 10 findnearest request?
        
    def KILL(self, event):
        #navId = event.data()[1]
        self.logger.debug("Received kill message")
        self.node.exit()

class Connecting(State):
    """ We are trying to connect to the Solipsis world """
            
    def NEAREST(self, event):
        """
        A peer sent us a NEAREST message
        """
        # create a find nearest event
        factory = EventFactory.getInstance()
        findnearest = factory.createFindnearestEvt()    
        
        findnearest.setRecipient(event.getSenderAddress())
        self.node.fire(findnearest)
        # since we know at least one peer, we leave the not connected state and go
        # to the moving state
        self.node.setState('Moving')

    def BEST(self, event):
        # TODO
        self.node.setState('Turning')

class Moving(State):
    def NEAREST(self, event):
        """
        A peer sent us a NEAREST message
        """
        findnearest = Event.createEvent(Event.PEER, Request.FINDNEAREST)
        findnearest.setRecipient(event.getAddress())
        self.node.fire(findnearest)
        


class Idle(State):

    def FINDNEAREST(self, event):

        targetPosition = Postion()
        targetPosition.setValueFromString(event.getArg('Position'))
        nearestPeer = self.node.getPeersManager().getClosestPeer(target)
        
        factory = EventFactory.getInstance()
        
        # check if I am not closer than nearestPeer
        if (self.node.isCloser(nearestPeer, target)):
            # send a BEST message
            response = factory.createBestEvt()
        else:
            response = factory.createNearestEvt(nearestPeer)

        response.setRecipientAddress(event.getSenderAddress())
        
        # send reply to remote peer
        self.node.fire(response)
