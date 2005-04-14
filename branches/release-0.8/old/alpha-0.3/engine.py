## SOLIPSIS Copyright (C) France Telecom

## This file is part of SOLIPSIS.

##    SOLIPSIS is free software; you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as published by
##    the Free Software Foundation; either version 2.1 of the License, or
##    (at your option) any later version.

##    SOLIPSIS is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU Lesser General Public License for more details.

##    You should have received a copy of the GNU Lesser General Public License
##    along with SOLIPSIS; if not, write to the Free Software
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

## ------------------------------------------------------------------------------
## -----                           engine.py                               -----
## ------------------------------------------------------------------------------


from threading import Thread
import sys, time
from Queue import Queue
from socket import socket, AF_INET, SOCK_DGRAM
import select

from peer import Peer
from event import PeerEvent
from util import Geometry


class Engine:
  
  def __init__(self, _node, logger):
    
    self.node = _node
    self.version = "0"
    self.logger = logger

  def encodeMsg(self, args):
    """ create a message with the arguments given """
    return PeerEvent(args)
  
class V0_2_5_Engine(Engine):
  def __init__(self, _node, params):
    """ Constructor.
    node: the node associated with this engine"""
    logger = params[0]
    Engine.__init__(self, _node, logger)
    
    # all the possible states of the node
    self.state = State("NOT_CONNECTED")

    # version of the protocol
    self.version = "0.2.5"

  def process(self, event):
    """ Process an event.
    event : the event to be processed """

    if ( event.type() == "peer" ):
      self.processPeerEvent(event)
    elif ( event.type() == "control" ):
      self.processControlEvent(event)
    else:            
      self.logger.critical("unknow event type " + event.type())

  def processPeerEvent(self, event):
    """ We have received a message from a peer, process this message
    event : the event containing the message sent by a peer """
    name = event.name()
    args = event.args()
    self.logger.debug("event name %s - event args %s", name, args)
    manager = self.node.getPeersManager()
    # check 
    peer = manager.getPeerFromAddress(event.senderAddress())
    self.logger.debug("senderAddress " + event.senderAddress())
    if not peer:
      peer = manager.createPeer(event.senderAddress())
      
    # TODO : check parameters of messages, and current state of the node
    #        check if sender of message and ID of message matches
    #
    # E.g.: if we receive a best message and we are not in the moving state
    #       discard message
    if ( name == "FINDNEAREST" ):
      # FINDNEAREST, host, port, posX, posY
      [posX, posY] = [args[2], args[3]]
      OnFindnearest(peer, posX, posY)
      
    elif ( name == "NEAREST" ):
      if((self.state.name == "MOVING") or (self.state.name == "TURNING")):
        [id, host, port, positionX, positionY] = args
        nearest = Peer(id, host, port, [positionX, positionY])
                  
        # if detected nearest entity is closer than last Nearest
        if( not self.state.neighbours or 
            nearest.isCloser(self.state.neighbours[0], self.node.position) ):
          self.OnNearest(nearest)
          
    elif ( name == "BEST" ):
      if((self.state.name == "MOVING") or (self.state.name == "TURNING")):
        [id, host, port, positionX, positionY] = args
        best = Peer(id, host, port, [positionX, positionY])
        if( not self.state.neighbours or
            best.isCloser(self.state.neighbours[0], self.node.position)
            or best.getId() == self.state.neighbours[0].getId() ):
          self.OnBest(best)
          
    elif ( name == "QUERYAROUND" ):
      [id, host, port, positionX, positionY, idNearest, distNearest] = args    
      queryPeer =  Peer(id, host, port, [positionX, positionY])
      # TODO : check if peer == queryPeer
      self.OnQueryaround(queryPeer, idNearest, distNearest)
      
    elif ( name == "AROUND" ):
      if(self.state.name == "TURNING"):
        [id, host, port, positionX, positionY] = args
        around = Peer(id, host, port, [positionX, positionY])
        self.OnAround(around)
      
    elif ( name == "HEARTBEAT" ):
      id = peer.getId()
      OnHeartbeat(id)
      
    elif ( name == "HELLO" ):
      [id, host, stringPort, stringPosX, stringPosY, stringAR, stringCa,
       pseudo, stringORI ] = args
      helloPeer = Peer(id, host, stringPort, [stringPosX, stringPosY], stringAR,
                       stringCa, pseudo, stringORI)
      self.OnHello(helloPeer)
      
    elif ( name == "CONNECT" ):
      [id, host, stringPort, stringPosX, stringPosY, stringAR, stringCa,
       pseudo, stringORI ] = args
      connectPeer = Peer(id, host, stringPort, [stringPosX, stringPosY], stringAR,
                         stringCa, pseudo, stringORI)
      self.OnConnect(connectPeer)
      
    elif ( name == "SERVICE" ):
      OnService(event)
      
    elif ( name == "ENDSERVICE" ):
      OnEndservice(event)
      
    elif ( name == "DELTA" ):
      OnDelta(event)
      
    elif ( name == "DETECT" ):
      OnDetect(event)
      
    elif ( name == "SEARCH" ):
      OnSearch(event)
      
    elif ( name == "FOUND" ):
      OnFound(event)
      
    elif ( name == "CLOSE" ):
      OnClose(event)
      
    else:
      self.node.logger.critical("unknow event name " + name)
      # Probably the bootstrap message
      self.OnBootstrap(peer, name,args)

  def OnBootstrap(self, peer, name, args):
    myIp = name
    [myPort, peerIp, peerPort] = args
    self.node.host = myIp
    self.node.port = int(myPort)
    self.node.createId()
    self.state.name = "MOVING"
    self.node.send(peer, self.FindnearestMsg())
  
  def OnHeartbeat(self, id):
    """ reception of a message: HEARTBEAT, id"""
    self.node.getPeersManager().heartbeat(id)
  
  def OnFindnearest(self, peer, stringPosX, stringPosY):
    """  return the entity that is the closest to the position target
    peer : the entity sending the request
    posX, posY : 2 strings representing the position target 
    """
    target = [long(stringPosX), long(stringPosY)]
    nearestPeer = self.node.getPeersManager().getClosestPeer(target)

    # check if I am not closer than nearestPeer
    if (self.node.isCloser(nearestPeer, target)):
      # send a BEST message
      msg = self.BestMsg()
    else:
      msg = self.NearestMsg(peer)

    # send reply to remote peer
    self.node.send(peer, msg)

  def OnQueryaround(self, peer, idNearest, distNearest):
    manager = self.node.getPeersManager()
    target = peer.position
    closest = manager.getClosestPeer(target)
    # found a closest peer and this peer is a new one (it isn't idNearest moving
    # toward target position).    
    if ( (Geometry.distance(closest.position, target) < distNearest) and
         closest.id <> idNearest ):
      # send a nearest message
      msg = self.NearestMsg(closest)
      self.node.send(peer, msg)
    # search for a peer around target position  
    else:
      around = manager.getPeerAround(self.node.position, target)
      if around:
        msg = self.AroundMsg(around)
        self.node.send(peer, msg)
        
  def OnNearest(self, peer):
    self.state.neighbours = [peer]    
    # while turning, we found a closer entity : go back to moving state
    if( self.state.name == "TURNING" ):
      self.state.name = "MOVING"        

    msg = self.FindnearestMsg()
    self.node.send(peer, msg)

  def OnBest(self, peer):
    self.state.neighbours = [peer]
    # while turning, we found a closer entity : go back to moving state
    if( self.state.name == "TURNING" ):
      self.state.name = "MOVING"
      msg = self.FindnearestMsg()
      self.node.send(peer, msg)
    # we found the closest entity, we now have to turn around this entity
    elif ( self.state.name == "MOVING" ):
      self.state.name = "TURNING"
      distance = Geometry.distance(peer.position, self.node.position)
      msg = self.QueryaroundMsg(peer.id, distance)
      self.node.send(peer, msg)

  def OnAround(self, peer):
    nbNeighbours = len(self.state.neighbours)
    # last neighbour found
    last = self.state.neighbours[nbNeighbours-1]
    # best neighbour
    best = self.state.neighbours[0]

    peerPosition = Geometry.relativePosition(peer.position, self.node.position)
    # check if turn ends : we have at least 3 neighbours and either we got back
    # to the first peer (=> turn completed) or our last neighbour was in the left
    # half plane and this peer is in the right half plane
    if ( nbNeighbours > 2 ) and (peer.id == best.id) or (
      not Geometry.inHalfPlane(best.position, self.node.position, last.position)
      and Geometry.inHalfPlane(best.position, self.node.position, peerPosition) ):
        self.state.name = "CONNECTING"      
        # Our awarenesse radius is the distance between us and our closest neighbour,
        # because we are sure to know all the entities between us and the best.
        bestRelativePos = Geometry.relativePosition(best.position,
                                                    self.node.position)
        minDistance = Geometry.distance(bestRelativePos, self.node.position)
        self.node.updateAr(minDistance)

        # register these peers with the peerManager and connect !
        manager = self.node.getPeersManager()
        for p in self.state.neighbours:
          manager.addPeer(p)
          msg = self.HelloMsg()
          self.node.send(p, msg)
      
    else:
      # add this peer to our list of neighbours
      self.state.neighbours.append(peer)
      bestDist = Geometry.distance(best.position, self.node.position)
      msg = self.QueryaroundMsg(best.id, bestDist)
      # send this peer a queryaround message
      self.node.send(peer, msg)


  def OnHello(self, peer):
    """ HELLO, id, host, port, positionX, positionY,awareness radius, caliber,
    pseudo, ori'"""
    manager = self.node.getPeersManager()    
    manager.addPeer(peer)
    
    # we have too many peers
    if manager.hasTooManyPeers():
      # select worst peer, send him a CLOSE message and remove it
      worst = manager.getWorstPeer()
      closeMsg = self.CloseMsg()
      self.node.send(worst, closeMsg)
      manager.removePeer(worst)
      
      # connect to the new peer only if it is not the worst one
      if not worst.id == peer.id:
        connectMsg = self.ConnectMsg()
        self.node.send(peer, connectMsg)      
    else:
      connectMsg = ConnectMsg()
      self.node.send(peer, connectMsg)
    
  def OnConnect(self, peer):
    """ CONNECT, id, host, port, positionX, positionY, awareness radius, caliber,
    pseudo, ori'"""
    manager = self.node.getPeersManager()
    manager.updatePeer(peer)
    self.logger.critical("OnConnect NOT IMPLEMENTED")

    
  ##########################################################################
  # SOLIPSIS messages for v0.2.5
  # 
  # best, service, endservice, connect, hello, close, delta, heartbeat
  # around, queryaround, detect, search, found, findnearest, nearest
  ##########################################################################
  def BestMsg(self):
    """ Create a BEST message.
    BEST host, port, posX, posY
    """
    args = ["BEST"] + self.node.getConnectInfo()
    return self.encodeMsg(args)

  def ServiceMsg(self, serviceId):
    """ SERVICE, id, id_service, descr, host, port"""
    srv = self.node.service[service_id]
    args = ["SERVICE", self.node.id, serviceId, srv.desc, srv.host, str(srv.port) ]
    return self.encodeMsg(args)

  def EndserviceMsg(self, serviceId):
    """ ENDSERVICE, id, id_service """
    args = ["ENDSERVICE", self.node.id, serviceId]
    return self.encodeMsg(args)

  def ConnectMsg(self):
    """ CONNECT, id, host, port, positionX, positionY, awareness radius,
    caliber, pseudo, ori"""
    args = ["CONNECT"] + self.node.getAllInfo()
    return self.encodeMsg(args)

  def HelloMsg(self):
    """ HELLO, id, host, port, positionX, positionY, awareness radius,
    caliber, pseudo, ori'"""
    args = ["HELLO"] + self.node.getAllInfo()
    return self.encodeMsg(args)

  def CloseMsg(self):
    """ CLOSE, id """
    args = ["CLOSE", self.node.id]    
    return self.encodeMsg(args)

  def DeltaMsg(self, name):
    """DELTA, id, var, newVar
    var is the modified variable: 'POS' or 'AR' or 'ORI'"""
    if ( name == "POS" ):
      var = self.node.position
    elif ( name == "ORI" ):
      var = self.node.orientation
    elif ( name == "AR"):
      var = self.node.awarnessRadius

    args = ["DELTA", self.node.id, name, var]
    return self.encodeMsg(args)

  def HeartbeatMsg(self):
    """ HEARTBEAT id """
    args = ["HEARTBEAT", self.node.id]
    return self.encodeMsg(args)

  def DetectMsg(self, peer):
    """ DETECT, id, host, port, positionX, positionY, awareness radius,
    caliber, pseudo """
    args = [ "DETECT", peer.id] +  peer.getConnectInfo() + [
      peer.awarenessRadius, peer.caliber, peer.pseudo ]
    return self.encodeMsg(args)

  def FoundMsg(self, peer):
    """FOUND, id, host, port, posX, posY, awareness radius, caliber, pseudo""" 
    args = ["FOUND", peer.id] +  peer.getConnectInfo() + [
      peer.awarenessRadius, peer.caliber, peer.pseudo ]
    return self.encodeMsg(args)

  def SearchMsg(self, isCounterclockwise):
    """ SEARCH, id, wise = 1 if counterclockwise"""
    args = ["SEARCH", self.node.id, isCounterclockwise]
    return self.encodeMsg(args)

  def FindnearestMsg(self):
    """ FINDNEAREST, host, port, posX, posY"""
    args = ["FINDNEAREST"] + self.node.getConnectInfo() 
    self.logger.debug(self.encodeMsg(args))
    return self.encodeMsg(args)

  def QueryaroundMsg(self, idNearest, distNearest):
    """ QUERYAROUND, id, host, port, posX, posY, id_nearest, dist_nearest """
    args = ["QUERYAROUND", self.node.id] +  self.node.getConnectInfo()
    args = args + [idNearest, str(distNearest)]
    
    return self.encodeMsg(args)

  def NearestMsg(self, peer):
    """ NEAREST, id, host, port, positionX, positionY"""
    args = ["NEAREST", peer.id] + peer.getConnectInfo()
    return self.encodeMsg(args)

  def AroundMsg(self, peer):
    """ AROUND, id, host, port, positionX, positionY"""
    args = ["AROUND", peer.id] + peer.getConnectInfo() 
    return self.encodeMsg(args)

class State:
  # STATES = {"NOT_CONNECTED":0, "IDLE":1, "MOVING":2, "TURNING":3}
  def __init__(self, name):
    self.name = name
    self.best = None
    self.neighbours = []
