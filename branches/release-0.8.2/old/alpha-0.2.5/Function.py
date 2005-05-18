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
## -----                           Function.py                              -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   We find in this module all functions used by the entity.
##
## ******************************************************************************

from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
import string
import math
import sys
import threading

import globalvars
import Entity

#################################################
#                 isAlive                       #
#################################################

def isAlive():
  """ return TRUE if ALIVE"""
  
  return globalvars.ALIVE

#################################################
#                 createEntity                  #
#################################################

def createEntity(id, host, port, pos, ori, awareness_radius, caliber, pseudo, answer = "HELLO"):
  """ create an entity if it is not choose for remove 
  and send a message HELLO to it. The pos of the new entity 
  must be in the local bench mark"""

  if globalvars.me.adjacents.has_key(id):

    # entity already known
    return 0

  # create new entity
  new_entity = Entity.Entity(id, host, port, pos, ori, awareness_radius, caliber, pseudo)
  
  # updates list of adjacents
  globalvars.me.adjacents[id] = new_entity
  globalvars.me.distAdjacents.ins(new_entity)
  globalvars.me.ccwAdjacents.ins(new_entity)
  
  # determine worst entity among neighbors
  worst_entity = chooseForRemove()
  
  if len(globalvars.me.adjacents) > globalvars.me.exp and worst_entity == new_entity:
    
    # we are not interested by this new entity
    del globalvars.me.adjacents[id]
    globalvars.me.distAdjacents.delete(new_entity)
    globalvars.me.ccwAdjacents.delete(new_entity)

    # connection refused
    if answer == "CONNECT":
      message = encodeMsg( [ "CLOSE",globalvars.me.ident ] )
      new_entity.sendNetworkMessage(message)

    return 0
    
  # send a message answer
  listHello = [answer, globalvars.me.ident, globalvars.me.host, str(globalvars.me.network_port), str(globalvars.me.position[0]), str(globalvars.me.position[1]), str(globalvars.me.awareness_radius), str(globalvars.me.caliber), globalvars.me.pseudo, str(globalvars.me.ori)]
  message = encodeMsg(listHello)
  new_entity.sendNetworkMessage(message)

  # confirm entity if the message is connect
  if answer == "CONNECT":
    new_entity.confirm(pos, ori, awareness_radius, caliber, pseudo)
        
  # close worst entity if too many neighbors
  if len(globalvars.me.adjacents) > globalvars.me.exp and worst_entity:
    worst_entity.sendNetworkMessage(encodeMsg(["CLOSE", globalvars.me.ident]))
    closeConnection(worst_entity)      

  return new_entity

#################################################
#               closeConnection                 #
#################################################

def closeConnection(entity):
  """ close the connection with entity  """
  print "Function.closeConnection(%s)" %entity.id
  if globalvars.me.adjacents.has_key(entity.id):
    globalvars.me.ccwAdjacents.delete(entity)
    globalvars.me.distAdjacents.delete(entity)
    del globalvars.me.adjacents[entity.id]

    # send message to media modules if entity confirmed
    if entity.ok:
      if globalvars.me.GUIConnected:
        for media in globalvars.me.media.values():
          if media.push:
            if media.thread.deadNode(entity.id) == -1:
              sys.stderr.write("error in deadNode "+ entity.pseudo+"\n")
              if media.addBug():
                del globalvars.me.media[media.id]
            else:
              media.bug = 0

#################################################
#               chooseForRemove                 #
#################################################
def chooseForRemove():
  """ choose an entity with which connection will be closed
  return an entity and 0 if no entity can be removed"""

  # filter list of neighbors
  # keep only entities not in Awareness Area which do not provoke mis-respect
  # of Global Connectivity Rule

  FilterList = []
  endFilter = 1
  indexFilter = globalvars.me.distAdjacents.length - 1

  while endFilter and indexFilter > 0:
    ent = globalvars.me.distAdjacents.ll[indexFilter]
    distEnt = distance(ent.local_position, [0, 0])
        
    # first, verify that ent is not in Awareness Area
    if distEnt > globalvars.me.awareness_radius :
      if distEnt > ent.awareness_radius:

	indInCcw = globalvars.me.ccwAdjacents.ll.index(ent)
        successor = globalvars.me.ccwAdjacents.ll[(indInCcw + 1) % globalvars.me.ccwAdjacents.length]
        predecessor = globalvars.me.ccwAdjacents.ll[indInCcw - 1]

        # then verify that ent is not mandatory for Rule respect
	if inHalfPlane(predecessor.local_position, [0, 0], successor.local_position):
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

#################################################
#                  detectionCheck               #
#################################################

def detectionCheck(new_entity):
  """ check if new_entity may interest some other entities"""
  
  # compute my distance to newEnt
  myDistToNew = distance([0, 0], new_entity.local_position)

  for ent in globalvars.me.adjacents.values():
    if ent <> new_entity:

      # compute the distance between new_entity and ent
      theirDist = distance(ent.position, relativePosition(new_entity.position, ent.position))

      if theirDist < ent.awareness_radius or theirDist < myDistToNew or theirDist < new_entity.awareness_radius:

        # send DETECT new_entity to ent
        list = ["DETECT", new_entity.id, new_entity.host, str(new_entity.port), str(new_entity.position[0]), str(new_entity.position[1]), str(new_entity.awareness_radius), str(new_entity.caliber), new_entity.pseudo]
        message = encodeMsg(list)
        ent.sendNetworkMessage(message)


#################################################
#		    ccwOrder		        #
#################################################

def ccwOrder(x, y, pos):
  """ return TRUE if entity y is before entity x in ccw order relation to position pos"""
  
  # take the p-relative position of x and y
  xx = relativePosition(x.position, pos)
  yy = relativePosition(y.position, pos)

  # verify that they lie in the same half-plane (up or down to pos)
  upX = xx[1] - pos[1] <= 0
  upY = yy[1] - pos[1] <= 0

  if upX <> upY:
    # they do not lie to the same half-plane, y is before x if y is up
    result = upY
  else:
    # they lie in the same plane, compute the determinant and check the sign
    result = not inHalfPlane(xx, pos, yy)
    
  return result

#################################################
#		   distOrder		        #
#################################################

def distOrder(x, y, pos):
  """ return TRUE if entity y is closer to position pos than entity x"""

  # take the p-relative position of x and y
  xx = relativePosition(x.position, pos)
  yy = relativePosition(y.position, pos)
    
  return ( distance(yy, pos) < distance(xx, pos) )

#################################################
#                   decodeMsg                   #
#################################################

def decodeMsg(msg):
  """ decode message msg and return a list of params"""
  return msg.split(";")[1:]

  
#################################################
#                   encodeMsg                   #
#################################################

def encodeMsg(list):
  """ encode list of string list and return a string"""
  return ";".join(list)
  

#################################################
#                  inHalfPlane                  #
#################################################

def inHalfPlane(p1, p2, pos):
  """ compute if pos belongs to half-plane delimited by (p1, p2)
  p2 is the central point for ccw
  return boolean TRUE if pos belongs to half-plane"""
  return (pos[0]-p1[0])*(p1[1]-p2[1]) + (pos[1]-p1[1])*(p2[0]-p1[0]) > 0

#################################################
#                  distance                     #
#################################################

def distance(p1, p2):
  """ compute euclidean distance for the minimal geodesic between two positions p1 and p2"""
  return long ( math.hypot( p1[0]-p2[0], p1[1]-p2[1] ) )

#################################################
#              relativePosition                 #
#################################################

def relativePosition(pos, ref = [0, 0]):
    """ return the relative position of pos (relative to ref)"""
    
    result = [pos[0], pos[1]]

    #-----Step 1: x-axis
    
    if pos[0] > ref[0]:
        if pos[0] - ref[0] > globalvars.SIZE/2:
            result[0] = pos[0] - globalvars.SIZE
    else:
        if ref[0] - pos[0] > globalvars.SIZE/2:
            result[0] = pos[0] + globalvars.SIZE

    #-----Step 2: y-axis
    
    if pos[1] > ref[1]:
        if pos[1] - ref[1] > globalvars.SIZE/2:
            result[1] = pos[1] - globalvars.SIZE
    else:
        if ref[1] - pos[1] > globalvars.SIZE/2:
            result[1] = pos[1] + globalvars.SIZE

    return result

#################################################
#		 killAllThread                  #
#################################################

def killAllThread():

  # send a message to the udp socket before quiting
  killSocket = socket( AF_INET, SOCK_DGRAM )
  killSocket.bind( (globalvars.me.host, 32145) )
  killSocket.sendto( "KILL", (globalvars.me.host, globalvars.me.network_port) )
  killSocket.close()

  # send a message to the udp socket before quiting  
  killSocket = socket( AF_INET, SOCK_STREAM )
#  killSocket.bind( (globalvars.me.host, 32145) )
  killSocket.connect( (globalvars.me.host, globalvars.me.GUI_port) )
  killSocket.send("KILL")
  killSocket.close()

