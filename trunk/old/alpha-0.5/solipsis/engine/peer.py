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
## -----                           Peer.py                                -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module defines the class for a neighbor.
##   A neighbor is an entity with which we are able to communicate.
##   This module provides all methods for the modifications of any variable
##   characteristic of an entity.
##   These modifications are capted by the Network module.
##
## ******************************************************************************

import random, string, time
from solipsis.engine.entity import Entity, Position, Address
from solipsis.util.exception import SolipsisInternalError
from solipsis.util.util import CcwList, DistList, Geometry

#################################################################################################
#                                                                                               #
#			----- Information about an entity ---------				#
#                                                                                               #
#################################################################################################

class Peer(Entity):
  
  def __init__(self, id="", host="", port=0, pos=Position(0,0), ori=0,
               awareness_radius=0, caliber=0, pseudo=""):
    """ Create a new Entity and keep information about it"""

    # call parent class constructor
    Entity.__init__(self,pos, ori, awareness_radius, caliber, pseudo)

    self.id   = id
    self.address = Address(host, port)
    
    # last time when we saw this peer active 
    self.activeTime = 0

    # local position is the position of this peer using a coordinate system
    # centered on the position of the node
    # this value is set-up by the peer manager
    self.localPositon = pos
    
    # set the ID of this peer
    #id = self.createId()
    #self.setId(id)
    
    # position and relative position
    #relative_position = Function.relativePosition(self.position,
    # globalvars.me.position)
    #self.local_position = [ relative_position[0] - globalvars.me.position[0],
    #relative_position[1] - globalvars.me.position[1] ]

    # two boolean variables indicating that
    # we received a message from this entity
    self.message_received = 1
    # we sent a message to this entity
    self.message_sent = 0

    # services provided by entity
    # {id_service: [desc_service, host, port], ...}
    self.services = {}
    
    # boolean confirmation of the accuracy of informations
    self.ok = 0

  def isCloser(self, peerB, targetPosition):
    """ Return True if this peer is closer than peerB to targetPosition
    """
    d1 = Geometry.distance(self.position, targetPosition)
    d2 = Geometry.distance(peerB.position, targetPosition)
    print "isCloser d1= %s d2= %s" %(str(d1), str(d2))
    return ( Geometry.distance(self.position, targetPosition) <
             Geometry.distance(peerB.position, targetPosition) )

  def setLocalPosition(self, nodePosition):
    """ Set the local position in the coordinate system with origin nodePosition
    nodePoistion: position of the node, e.g. [12,56]
    """
    self.localPosition = Geometry.localPosition(self.position, nodePosition)

  def setActiveTime(self, t):
    self.activeTime = t
    
  def addService(self, id_service, desc_service, host, port):
    """ add a new service"""
    # TODO
    self.services[id_service] = [desc_service, host, port]

    

  def closeService(self, id_service):
    """ delete service"""
    # TODO
    if self.services.has_key(id_service):
      del self.services[id_service]


  def updateOri(self, new_ori):
    """ update entity orientation """
    # TODO
    self.ori = int(new_ori)

    # send message to Media
    if globalvars.me.GUIConnected:
      stringVar = "ORI"
      stringVariation = str(self.ori)
      for media in globalvars.me.media.values():
        if media.push:
          resul = media.thread.modNode(self.id, stringVar, stringVariation)
          if not resul:
            if media.thread.newNode(self.id, self.local_position[0], self.local_position[1], self.caliber, self.pseudo, self.ori) == -1:
              sys.stderr.write("error in modNode updateOri")
              if media.addBug():
                del globalvars.me.media[media.id]
            else:
              media.bug = 0
          elif resul == -1:
            if media.addBug():
                del globalvars.me.media[media.id]
          else:
            media.bug = 0

    
  def updatePos(self, new_pos):
    """ update the position of the entity"""
    # TODO
    
    # update position
    old_position = self.position
    self.position = new_pos
    relative_position = Function.relativePosition(self.position, globalvars.me.position)
    self.local_position = [ long(relative_position[0] - globalvars.me.position[0]), long(relative_position[1] - globalvars.me.position[1]) ]

    # compute delta
    delta_pos = []
    delta_pos.append(self.position[0] - old_position[0])
    delta_pos.append(self.position[1] - old_position[1])

    # update lists
    globalvars.me.ccwAdjacents.replace(self)
    globalvars.me.distAdjacents.replace(self)

    # send message to Media
    if globalvars.me.GUIConnected:
      stringVar = "POS"
      stringVariation = str(delta_pos[0]) + ", " + str(delta_pos[1])
      for media in globalvars.me.media.values():
        if media.push:
          resul = media.thread.modNode(self.id, stringVar, stringVariation)
          if not resul:
            if media.thread.newNode(self.id, self.local_position[0], self.local_position[1], self.caliber, self.pseudo, self.ori) == -1:
              sys.stderr.write("error in modNode updateOri")
              if media.addBug():
                del globalvars.me.media[media.id]
            else:
              media.bug = 0
          elif resul == -1:
            if media.addBug():
                del globalvars.me.media[media.id]
          else:
            media.bug = 0
    

  def confirm(self, pos, ori, ar, ca, pseudo):
    """ confirm and update informations: to detect liars"""
    # TODO
    self.ok = 1
    
    # update informations about this entity.
    self.position = pos
    relative_position = Function.relativePosition(self.position, globalvars.me.position)
    self.local_position = [ relative_position[0] - globalvars.me.position[0], relative_position[1] - globalvars.me.position[1] ]
    self.awareness_radius = ar
    self.pseudo = pseudo
    self.caliber = ca
    self.ori = ori
    
    # send informations to media
    if globalvars.me.GUIConnected:
      for media in globalvars.me.media.values():
        if media.push:
          if media.thread.newNode(self.id, self.local_position[0], self.local_position[1], self.caliber, self.pseudo,self.ori) == -1:
            sys.stderr.write("error in newNode "+self.pseudo+"\n")
            if media.addBug():
              del globalvars.me.media[media.id]
          else:
            media.bug = 0


    # we save a trace of this entity for further connection
    globalvars.me.met[(self.host,self.port)] = 1
    globalvars.me.nb_met += 1
              
    return 1


  def updateReference(self):
    """ Set up the position when the local node move."""
    
    # The node is the center of a local bench mark.
    relative_position = Function.relativePosition(self.position, globalvars.me.position)
    self.local_position = [ long(relative_position[0] - globalvars.me.position[0]), long(relative_position[1] - globalvars.me.position[1]) ]


class PeersManager:
  """ Manage all the neighbours of a node """
  def __init__(self, node, peersParams):
    """ Constructor
    node : node using this manager
    peersParams : initialization parameters of the peer manager, a list
    [entitiesFileName, maxPeers, logger]
    """
    self.node = node    
    self.entitiesFileName = peersParams[0]
    self.maxPeers = peersParams[1]
    self.logger = peersParams[2]

    # hash table of peers indexed by ID
    self.peers     = {}
    # clountercloclwise ordered list of peers 
    self.ccwPeers  = CcwList()
    # distance ordered list of peers
    self.distPeers = DistList()


  def createPeer(self, netAddress):
    """ create a new Peer object
    netAddress : the network address of this peer, e.g. '193.168.25.36:2456'
    Return a Peer object"""
    host = netAddress.getHost()
    port = netAddress.getPort()
    p = Peer('', host, port)
    p.createId()
    return p
    
  def getRandomPeer(self):
    """ Return a peer randomly chosen from a file
    Read the entities file and return a random peer
    """
    try:
      f = file(self.entitiesFileName, 'r')
    
      # read file
      list = f.readlines()
    
      # retrieve peer
      peer = random.choice(list)
      host, stringPort = string.splitfields(peer)
      port = int(stringPort)
      address = Address(host, port)
      f.close()
    except:
      self.logger.critical("Cannot read file " + self.entitiesFileName)
      raise
    p = Peer('', host, port)
    p.createId()
    return p
    
  def addPeer(self, p):
    """ add a new peer
    p : a peer object
    """
    referencePosition = self.node.position
    p.setLocalPosition(referencePosition) 

    id = p.getId()
    if not id:
      raise SolipsisInternalError("Error peer has no id")

    if self.peers.has_key(id):
      raise SolipsisInternalError("Error duplicate peer id:" + id)

    self.peers[p.getId()] = p
    
    self.ccwPeers.insert(p)
    self.distPeers.insert(p)

  def removePeer(self, p):
    """ remove a peer
    p : peer to remove """
    
    id = p.getId()
    if not id:
      raise SolipsisInternalError("Error peer has no id")

    if not self.peers.has_key(id):
      raise SolipsisInternalError("Error removing peer - no peer with id:" + id)
    
    del self.peers[id]
    self.ccwPeers.delete(p)
    self.distPeers.delete(p)

  def updatePeer(self, p):
    """ update information on a peer. """
    self.removePeer(p)
    self.addPeer(p)
    
  def getPeer(self, address):
    """ Return the peer associated with this net address """
    # TODO check exception if this peer doesn't exist
    id = address.toString()
    return self.peers[id]

  def heartbeat(self, id):
    """ Update status of a peer
    id : id of the peer that sent us a HEARTBEAT message
    """    
    peer = self.peers[id]
    peer.setActiveTime(time.time())

  def getPeerFromAddress(self, address):
    """ Get the peer with address 'address'
    address: address of the peer we are looking for - Address object
    Return : a peer, or None if no such peer was found
    """
    # Iterate through list of peers
    ids = self.peers.keys()
    for id in ids:
      p = self.peers[id]
      if p.address.toString() == address.toString():
        return p

    # no peer with this address was found
    return None
    

  def getClosestPeer(self, target):
    """ Return the peer that is the closest to a target position
    """
    closestPeer = self.peers.values()[0]
    for p in self.peers.values():
      if p.isCloser(closestPeer, target):
        closestPeer = p

    return closestPeer
      

  def getPeerAround(self, nodePosition, targetPosition):
    """ Return the peer that is the closest to a target position and that
    is in the right half plane.
    nodePosition : position of the node asking for a peer around
    targetPosition : target position which we are looking around
    Return : a peer
             or None if there is no peer in the right half plane
    """
    found = False
    around = None
    distClosest = 0
    
    for p in self.peers.values():
      if Geometry.inHalfPlane(nodePosition, targetPosition, p.position):
        # first entity in right half-plane
        if not found:
          found = True 
          around = p
          distClosest = Geometry.distance(targetPosition, p.position)
        else:
          dist = Geometry.distance(targetPosition, p.position)
          # this peer is closer
          if dist < distClosest:
            around = p
            distClosest = dist

    return around

  def hasTooManyPeers(self):
    """ Check if we have too many neighbours
    Return True if we have too many peers"""
    return len(self.peers) > self.maxPeers

  def getWorstPeer(self):
    """ Choose a peer for removal. Removing this must NOT break the global
    connectivity rule. """
    
    # filter list of neighbors
    # keep only entities not in Awareness Area which do not provoke mis-respect
    # of Global Connectivity Rule

    FilterList = []
    endFilter = 1
    indexFilter = self.distPeers.length - 1
    nodePos = self.node.position
    
    while endFilter and indexFilter > 0:
      ent = self.distPeers.ll[indexFilter]
      distEnt = Geometry.distance(ent.position, nodePos)
        
      # first, verify that ent is not in Awareness Area
      if distEnt > self.node.awarenessRadius :
        if distEnt > ent.awarenessRadius:

          indInCcw = self.ccwPeers.ll.index(ent)
          successor = self.ccwPeers.ll[(indInCcw + 1) % self.ccwPeers.length]
          predecessor = self.ccwPeers.ll[indInCcw - 1]

          # then verify that ent is not mandatory for Rule respect
          if Geometry.inHalfPlane(predecessor.position, nodePos,
                         successor.position):
	    FilterList.append(ent)
      
      else:
        # stop iteration because all following entities are in Awareness Radius
        endFilter = 0

      indexFilter -= 1

    if FilterList <> []:

      # there is a posibility to remove any entity in FilterList.
      # By default, we decide to remove the farthest entity.
      # In article presented at RESH'02, we proposed several other possibilities
      # for more efficient choice.
      result = FilterList[0]
    
    else:
      result = 0

    return result

  def enumerate(self):
    """ return a list with all peers """
    return self.distPeers

  def update(self):
    """ position of the node has changed rrecompute all neighbours postion """
    self.logger.critical("manager.update NOT IMPLEMENTED")
    raise SolipsisInternalError("manager.update NOT IMPLEMENTED")
