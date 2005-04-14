from solipsis.engine.engine import Engine
from solipsis.util.event import ControlEvent
from solipsis.util.exception import SolipsisInternalError

class ControlEngine(Engine):
    def __init__(self, _node, params):
        """ Constructor.
        node: the node associated with this engine"""
        logger = params[0]
        Engine.__init__(self, _node, logger)
        self._version = "0.3"
        
    def version(self):
        return self._version

    def process(self, event):
        type = event.data()[0]

        if( type == "nodeinfo"):
            nodeinfo = ControlEvent(self.node.getAllInfo())
            self.node.sendController(nodeinfo)
        elif( type == "peers"):
            manager = self.node.getPeersManager()
            peerList = manager.getAllPeers()
            #peers = ControlEvent(map(peerList,getInfo()))
            # TODO
            self.node.sendController(peers)
        elif( type == "peer"):
            id = event.data()[1]
            manager = self.node.getPeersManager()
            nodeinfo = ControlEvent(manager.getPeer(id).getInfo())
            self.node.sendController(nodeinfo)
        elif( type == "update" ):
            var   = event.data()[1]
            value = event.data()[2]
            if ( var == "POS"):
                # update position field
                oldPosition = self.node.position
                self.node.updatePosition(value)
                self.notifyUpdate(var, value)
                self.detectionCheck(oldPosition)
            elif( var == "ORI"):
                self.node.setOrientation(int(value))
                self.notifyUpdate(var, value)
            elif( var == "AR"):
                self.node.setAwarenessRadius(int(value))
                self.notifyUpdate(var, value)
            else:
                raise SolipsisInternalError("Update error unknow variable " + var)
        elif( type == "kill"):
            navId = event.data()[1]
            self.logger.debug("Received kill message from "+ str(navId))
            self.node.exit()
        else:
            self.logger.critical("Unnknown control message " + type)
            
    def notifyUpdate(self, var, value):
        """ Notify neighbours that our state has changed
        var : 'ORI' or 'AR' or 'POS'
        value : new value
        """
        manager = self.node.getPeersManager()
        # notify orientation to neighbors
        for peer in manager.getAllPeers():
          delta = self.DeltaEvent(var, value)
          self.node.send(peer, delta)



    def detectionCheck(self, old_position):
        """ Verify that self doesn't know an entity nearer to another"""
        manager = self.node.getPeersManager()
        listEnt = manager.getAllPeers()
        for ent in listEnt:
          i = listEnt.index(ent)

          # compute my distances to ent
          myDist = Geometry.distance(self.node.position, ent.position)
          myOldDist = Geometry.distance(old_position, ent.position)

          for ent2 in listEnt[i+1:]:

            # compute their distance
            theirDist = Geometry.distance(ent2.position, ent.position)

            # compute my distances to ent2
            myDist2 = Geometry.distance(self.node.position, ent2.position)
            myOldDist2 = Geometry.distance(old_position, ent2.position)

            if myDist > theirDist > myOldDist:
              # ent2 is now closer to ent than self
              # DETECT message sent to ent
              detect = DetectEvent(ent2)
              self.node.send(ent, detect)
              
            if myDist2 > theirDist > myOldDist2:
              # ent is now closer to ent2 than self
              # DETECT message sent to ent2
              detect2 = DetectEvent(ent)
              self.node.send(ent2, detect2)


    def DeltaEvent(self, var, value):
        return PeerEvent(["DELTA", self.node.getId(), var, value])

    def DetectEvent(self, ent):
        args = ["DETECT", ent.id, ent.position[0], ent.position[1], ent.awarenessRadius, ent.caliber, ent.pseudo]
        return PeerEvent(args)


class InternalEngine:
    def __init__(self, _node, params):
        """ Constructor.
        node: the node associated with this engine"""
        logger = params[0]
        Engine.__init__(self, _node, logger)

    def process(self, event):
        raise SolipsisInternalError("InternalEngine.process not implemented")
