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
## -----                           Network.py                               -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   The concern of this module is to allow the node to communicate with its
##   neighbor in order to form the netork of peers.
##   It allows the creation of a socket UDP for the message exchange
##   It provides all treatments for each message reception.
##
## ******************************************************************************

from threading import Thread
import string
import sys

from Function import *
import globalvars

#################################################################################################
#                                                                                               #
#			----- thread for the reception of messages ---------			#
#                                                                                               #
#################################################################################################

class Network_Reception(Thread):
  
  def __init__(self):
    Thread.__init__(self)

  def kill(self):
    pass
    
  def run(self):
    """ Receive messages from other nodes and process them"""

    while globalvars.ALIVE:

      try:
        # receive and process message from other nodes        
	data, add = globalvars.me.socket.recvfrom(2000)

        # decode the message and launch associated function
        name_function = data.split(";")[0]

        # special msg: KILL.
        if name_function == 'KILL':
          break

        # another special message: HI
        if name_function == 'HI':
          # have to remember who is the sender
          data = add

        # standard messages
        globalvars.mutex.acquire()
        eval(name_function)(data)
        globalvars.mutex.release()

      except:
        pass

    # close socket        
    globalvars.me.socket.close()
    print 'End of Network Server...'

   
#################################################################################################
#                                                                                               #
#			----- Some Functions invoked after reception of a msg ---------		#
#                                                                                               #
#################################################################################################

def HI(sender):
  """ reception of a message HI"""

  # respond by a message "itsHost, itsPort, myHost, myPort"
  its_host, its_port = sender
  message = encodeMsg( [str(its_host), str(its_port), str(globalvars.me.host), str(globalvars.me.network_port)] )
  globalvars.me.socket.sendto(message, sender)
  
#################################################
#                 HEARTBEAT	                #
#################################################

def HEARTBEAT(msg):
  """ reception of a message: HEARTBEAT, id"""
  
  id = decodeMsg(msg)[0]
  if globalvars.me.adjacents.has_key(id):
    globalvars.me.adjacents[id].message_received = 1

  # TODO -----------------------
  # re-connect in case of reception of heartbeat messages without knowledge of this node

#################################################
#                 SERVICE	                #
#################################################

def SERVICE(msg):
  """ reception of a message : 'SERVICE, id, id_service, descr, host, port' """

  # decode message
  try:
    id, id_service, descr, host, port = decodeMsg(msg)
  except:
    return

  if globalvars.me.adjacents.has_key(id) and not globalvars.me.adjacents[id].services.has_key(id_service):

    globalvars.me.adjacents[id].message_received = 1
    
    # add service for this entity
    globalvars.me.adjacents[id].addService(id_service, descr, host, port)
  
    # send service if id_service matche
    for media in globalvars.me.media.values():
        if id_service in media.services:
	  if media.push:
            if media.thread.service(id, id_service, descr, host, port) == -1:
              if media.addBug():
                sys.stderr.write("error in deadNode "+ entity.pseudo+"\n")
                del globalvars.me.media[media.id]
            else:
              media.bug = 0

	  # indicate to neighbor that a service matches
	  msg = encodeMsg(["SERVICE", globalvars.me.ident, id_service, media.services[id_service][0], media.services[id_service][1], media.services[id_service][2] ])
          globalvars.me.adjacents[id].sendNetworkMessage(msg)

#################################################
#                 ENDSERV	                #
#################################################

def ENDSERVICE(msg):
  """ reception of a message : 'ENDSERVICE, id, id_service' """
  
  # decode message
  try:
    id, id_service = decodeMsg(msg)
  except:
    return

  # delete service
  if globalvars.me.adjacents.has_key(id):
    globalvars.me.adjacents[id].message_received = 1
    globalvars.me.adjacents[id].closeService(id_service)

  # send a message to adequate media modules
  for media in globalvars.me.media.values():
    if id_service in media.services:
      if media.push:
        if media.thread.closeService(id, id_service) == -1:
          if media.addBug():
            sys.stderr.write("error in closeService\n")
        else:
          media.bug = 0
    
#################################################
#                 CONNECT	                #
#################################################

def CONNECT(msg):
  """ reception of a Connect msg = 'CONNECT, id, host, port, positionX, positionY, awareness radius, caliber, pseudo, ori'"""

  # decode message
  try:
    id, host, stringPort, stringPosX, stringPosY, stringAR, stringCa, pseudo, stringORI = decodeMsg(msg)
  except:
    return

  # no HELLO message sent or CONNECT message already received -> mistake !
  if not globalvars.me.adjacents.has_key(id) or globalvars.me.adjacents[id].ok:
    msg = encodeMsg(["CLOSE",globalvars.me.ident])
    globalvars.me.socket.sendto( msg, (host, port) )
    return

  # retrieve info
  port = int(stringPort)
  position = [long(stringPosX), long(stringPosY)]
  awareness_radius = long(stringAR)
  caliber = int(stringCa)
  ori = int(stringORI)

  # the entity
  ent = globalvars.me.adjacents[id]
  ent.message_received = 1
    
  # confirm and update informations    
  ent.confirm(position, ori, awareness_radius, caliber, pseudo)

  # update lists
  globalvars.me.ccwAdjacents.replace(ent)
  globalvars.me.distAdjacents.replace(ent)

  # send services
  for media in globalvars.me.media.values():
    for id_service in media.services:
      msg = encodeMsg(["SERVICE", globalvars.me.ident, id_service, media.services[id_service][0], media.services[id_service][1], str(media.services[id_service][2]) ])
      ent.sendNetworkMessage(msg)
        

#################################################
#                 HELLO			        #
#################################################

def HELLO(msg):
  """ reception of a Hello msg = 'HELLO, id, host, port, positionX, positionY, awareness radius, caliber, pseudo, ori'"""

  # decode message
  try:
    id, host, stringPort, stringPosX, stringPosY, stringAR, stringCa, pseudo, stringORI = decodeMsg(msg)
  except:
    return
  
  if not globalvars.me.adjacents.has_key(id):
    # retrieve informations
    position = [long(stringPosX), long(stringPosY)]
    awareness_radius = long(stringAR)
    caliber = int(stringCa)
    ori = int(stringORI)
    port = int(stringPort)

    # create new entity and confirm immediately
    createEntity(id, host, port, position, ori, awareness_radius, caliber, pseudo, "CONNECT")
  
#################################################
#		    CLOSE			#
#################################################

def CLOSE(msg):
  """ close connection with an entity
  reception of a message: CLOSE, id"""

  # decode message
  try:
    id = decodeMsg(msg)[0]
  except:
    return
  
  if globalvars.me.adjacents.has_key(id):
    closeConnection(globalvars.me.adjacents[id])

#################################################
#		    DELTA 			#
#################################################

def DELTA(msg):
  """ modification of a variable of an entity
  reception of message: DELTA, id, var, newVar
  var is the modified variable: 'pos' or 'ar' """

  # decode message
  try:
    id, stringVar, stringVariation = decodeMsg(msg)
  except:
    return
  
  # verify that this entity is known
  if not globalvars.me.adjacents.has_key(id):
    return

  # modified entity is modEnt
  modEnt = globalvars.me.adjacents[id]
  modEnt.message_received = 1

  # process the modification.
  if stringVar == "POS":
    
    # save old position
    old_position = modEnt.position
    
    # decode new position
    new_value = [long(e) for e in stringVariation.split(",")]

    if old_position == new_value:
      # no modification
      return

    modEnt.updatePos(new_value)
    
    # verify entities that could be interested by the entity id
    for ent in globalvars.me.adjacents.values():
                    
      # get distance between self and ent
      ourDist = distance([0,0], ent.local_position)
      
      # get distance between ent and entity id
      theirDist = distance(ent.position, relativePosition(modEnt.position, ent.position))
      
      # get old distance between ent and entity id
      theirOldDist = distance(ent.position, relativePosition(old_position, ent.position))
                    
      if theirDist < ent.awareness_radius < theirOldDist:
        # modified entity enters in Awareness Area of ent
                    
        # DETECT message sent to ent
        list = ["DETECT", modEnt.id, modEnt.host, str(modEnt.port), str(modEnt.position[0]), str(modEnt.position[1]), str(modEnt.awareness_radius), str(modEnt.caliber), modEnt.pseudo]
        message = encodeMsg(list)
        ent.sendNetworkMessage(message)
                    
      elif theirDist < ourDist and theirOldDist > ourDist:
        # moving entity is now closer than us to ent
            
        # DETECT message sent to ent
        list = ["DETECT", modEnt.id, modEnt.host, str(modEnt.port), str(modEnt.position[0]), str(modEnt.position[1]), str(modEnt.awareness_radius), str(modEnt.caliber), modEnt.pseudo]
        message = encodeMsg(list)
        ent.sendNetworkMessage(message)
        
      elif theirDist < modEnt.awareness_radius < theirOldDist:
        # ent enter in Awareness Area of moving entity

        # DETECT message sent to id
        list = ["DETECT", ent.id, ent.host, str(ent.port), str(ent.position[0]), str(ent.position[1]), str(ent.awareness_radius), str(ent.caliber), ent.pseudo]
        message = encodeMsg(list)
        modEnt.sendNetworkMessage(message)

  elif stringVar == "ORI" :
    new_ori = long(stringVariation)
    globalvars.me.adjacents[id].updateOri(new_ori)

  elif stringVar == "AR":
        
    # decode new awareness radius
    new_value = long(stringVariation)

    # save old Ar
    oldAR = modEnt.awareness_radius

    # modify value
    globalvars.me.adjacents[id].updateAr(new_value)

    # verify entities that could be interested by the modified entity.
    for ent in globalvars.me.adjacents.values():
      
      # get distance between ent and modified entity.
      theirDist = distance(ent.position, relativePosition(modEnt.position, ent.position))
      
      if oldAR < theirDist < modEnt.awareness_radius:
        # ent enter in Awareness Area of modified entity.
        # DETECT message sent to modified entity.
        list = ["DETECT", ent.id, ent.host, str(ent.port), str(ent.position[0]), str(ent.position[1]), str(ent.awareness_radius), str(ent.caliber), ent.pseudo]
        message = encodeMsg(list)
        modEnt.sendNetworkMessage(message)

#################################################
#                 DETECT                        #
#################################################

def DETECT(msg):
  """ a new entity is detected
  reception of message: DETECT, id, host, port, positionX, positionY, awareness radius, caliber, pseudo"""

  # decode message
  try:
    id, host, stringPort, stringPosX, stringPosY, stringAR, stringCa, pseudo = decodeMsg(msg)
  except:
    return
  
  if id <> globalvars.me.ident and not globalvars.me.adjacents.has_key(id):

    # create entity but do not confirm
    position = [long(stringPosX), long(stringPosY)]
    awareness_radius = long(stringAR)
    caliber = int(stringCa)
    port = int(stringPort)
   
    new_entity = createEntity(id, host, port, position, 0, awareness_radius, caliber, pseudo)

#################################################
#                 FOUND                         #
#################################################

def FOUND(msg):
  """ an entity detected in an empty sector
  reception of message: FOUND, id, host, port, posX, posY, awareness radius, caliber, pseudo"""
    
  # decode message.
  try:
    id, host, stringPort, stringPosX, stringPosY, stringAR, stringCa, pseudo = decodeMsg(msg)
  except:
    return

  # verify that new entity is neither self neither an already known entity.
  if id == globalvars.me.ident or globalvars.me.adjacents.has_key(id):
    return 

  # The node is the center of a local bench mark.
  position = [long(stringPosX), long(stringPosY)]    
  awareness_radius = long(stringAR)
  caliber = int(stringCa)
  port = int(stringPort)

  # create new entity.
  new_entity = createEntity(id, host, port, position, 0, awareness_radius, caliber, pseudo)

  # send msg SEARCH.
  bad_entities = globalvars.me.ccwAdjacents.checkGlobalConnectivity()
  for pair in bad_entities:
    # send message to each entity
    list1 = ["SEARCH", globalvars.me.ident, "1"]
    list2 = ["SEARCH", globalvars.me.ident, "0"]
    msg1 = encodeMsg(list1)
    msg2 = encodeMsg(list2)
                
    pair[0].sendNetworkMessage(msg1)
    pair[1].sendNetworkMessage(msg2)

#################################################
#                 SEARCH                        #
#################################################

def SEARCH(msg):
  """ search an entity to restore the global connectivity of an other node
  reception of message: SEARCH, id, wise = 1 if counterclockwise"""

  # decode message
  
  try:
    id, stringWise = decodeMsg(msg)
  except:
    return
  
  wise = int(stringWise)
  if not globalvars.me.adjacents.has_key(id):
    return

  # queryEnt is the querying entity
  queryEnt = globalvars.me.adjacents[id]

  queryEnt.message_received = 1
        
  # found is boolean TRUE if there is an adjacent in the sector
  found = 0

  # compute my relative position
  my_relative_position = relativePosition(globalvars.me.position, queryEnt.position)

  # find an entity: in the sector and near the entity.
  
  for ent in globalvars.me.adjacents.values():
    if ent.id <> id:

      their_relative_position = relativePosition(ent.position, queryEnt.position)
          
      if inHalfPlane(my_relative_position, queryEnt.position, their_relative_position) == wise:
        
          # ent is in the sector
          distEnt = distance(queryEnt.position, their_relative_position)
          if found:
            # we already found an entity in the sector
            # we keep e if e is the closest to p                
            if distFound > distEnt:
              entFound = ent
              distFound = distEnt
          else:
            # e is the first entity found in the sector                
            entFound = ent
            distFound = distEnt
            found = 1

  # send message if an entity has been found.
  
  if found:
      list = ["FOUND", entFound.id, entFound.host, str(entFound.port), str(entFound.position[0]), \
              str(entFound.position[1]), str(entFound.awareness_radius), str(entFound.caliber), entFound.pseudo]
      message = encodeMsg(list)
      queryEnt.sendNetworkMessage(message)

  
#################################################################################################
#                                                                                               #
#	  ----- Some Functions invoked for connexion and teleportation ---------        	#
#                                                                                               #
#################################################################################################

#################################################
#                 FINDNEAREST                   #
#################################################

def FINDNEAREST(msg):
  """  return the entity that is the closest to the position target
  reception of message:FINDNEAREST, host, port, posX, posY"""

  # decode message
  try:
    host, stringPort, stringPosX, stringPosY = decodeMsg(msg)
  except:
    return
  
  target = [long(stringPosX), long(stringPosY)]
  port = int(stringPort)

  if len(globalvars.me.adjacents) > 1:

    # check all adjacents
    
    # initialization
    entClose = globalvars.me.adjacents.values()[0]
        
    # check on the adjacent list
    for ent in globalvars.me.adjacents.values():
      if distOrder(entClose, ent, target):
	entClose = ent

    # check if I am not closer than entClose
    if distOrder(entClose, globalvars.me, target):
      list = ["BEST", globalvars.me.ident, globalvars.me.host, str(globalvars.me.network_port), str(globalvars.me.position[0]), str(globalvars.me.position[1])]

    else:
      # send the characteristics of entClose
      list = ["NEAREST", entClose.id, entClose.host, str(entClose.port), str(entClose.position[0]), str(entClose.position[1])]
      
    message = encodeMsg(list)
    globalvars.me.socket.sendto(message, (host, port))

#################################################
#               QUERYAROUND                     #
#################################################

def QUERYAROUND(msg):
  """ reception of message: QUERYAROUND, id, host, port, posX, posY, id_nearest, dist_nearest """

  # decode message
  try:
    id, host, stringPort, stringPosX, stringPosY, id_nearest, stringDistNearest = decodeMsg(msg)
  except:
    return

  port = int(stringPort)
  target = [long(stringPosX), long(stringPosY)]
  dist_nearest = long(stringDistNearest)

  myRelPos = relativePosition(globalvars.me.position, target)
  found = 0

  for ent in globalvars.me.adjacents.values():
        
    # compute relative position and distance
    posRel = relativePosition(ent.position, target)
    dist = distance(posRel, target)
        
    # check if ent is nearest to target than nearestPos
    if dist < dist_nearest and ent.id <> id_nearest: # and ent.id <> id:

      # send message to indicate a new nearest entity
      message = encodeMsg( [ "NEAREST", ent.id, ent.host, str(ent.port), str(ent.position[0]), str(ent.position[1]) ] )
      globalvars.me.socket.sendto(message, (host, port))

      # stop iteration
      return

    elif inHalfPlane(myRelPos, target, posRel):
      # ent is in the right half-plane
      if not found:
        # first entity detected in the half-plane
        found = 1
        entClose = ent
        distClose = dist
      elif dist < distClose:
        # verify if ent is closer than previously detected entity
        entClose = ent
        distClose = dist

  if found:
    # an entity in the half-plane found
    list = ["AROUND", entClose.id, entClose.host, str(entClose.port), str(entClose.position[0]), str(entClose.position[1])]
    message = encodeMsg(list)
    globalvars.me.socket.sendto(message, (host, port))


#################################################
#              NEAREST                          #
#################################################

def NEAREST(msg):
  """ reception of message: NEAREST, id, host, port, positionX, positionY"""
  
  # decode message
  try:
    id, host, stringPort, stringPosX, stringPosY = decodeMsg(msg)
  except:
    return

  port = int(stringPort)
  pos = [long(stringPosX), long(stringPosY)]

  posRel = relativePosition(pos, globalvars.me.position)
  dist = distance(posRel, globalvars.me.position)
  dist_nearest = globalvars.me.last_nearest[2]

  if globalvars.me.connected:
    # I am already connected, discard message
    return

  if globalvars.me.turning:

    if dist < globalvars.me.best[3]:
      # entity is closer than best ---> end of the turn
      
      # update variables
      globalvars.me.turning = 0
      globalvars.me.last_nearest = [host, port, dist]
      globalvars.me.best_entity = [-1, -1, -1, -1, [-1, -1]]
      globalvars.me.last_turn = [-1, -1, -1, [-1, -1]]
      globalvars.me.ent_to_connect = []

      # send message
      list = ["FINDNEAREST", globalvars.me.host, str(globalvars.me.network_port), str(globalvars.me.position[0]), str(globalvars.me.position[1])]
      message = encodeMsg(list)
      globalvars.me.socket.sendto(message, (host, port))

      return

    else:
      # discard message
      return

  # if detected nearest entity is closer than last Nearest
  if ( globalvars.me.last_nearest[0] == -1 ) or ( dist < dist_nearest ):

    # send FINDNEAREST message to entity
    list = ["FINDNEAREST", globalvars.me.host, str(globalvars.me.network_port), str(globalvars.me.position[0]), str(globalvars.me.position[1])]
    message = encodeMsg(list)
    globalvars.me.socket.sendto(message, (host, port))

    # update initialization variables
    globalvars.me.last_nearest = [host, port, dist]

#################################################
#              BEST                             #
#################################################

def BEST(msg):
  """ reception of message: BEST, id, host, port, positionX, positionY"""

  # decode message
  try:
    id, host, stringPort, stringPosX, stringPosY = decodeMsg(msg)
  except:
    return

  port = int(stringPort)
  pos = [long(stringPosX), long(stringPosY)]

  posRel = relativePosition(pos, globalvars.me.position)
  dist = distance(posRel, globalvars.me.position)

  if globalvars.me.connected:
    # I am already connected, discard message
    return
  
  if globalvars.me.turning:
    # I already found a best entity

    if dist < globalvars.me.best[3]:
      # entity is closer than best ---> end of the turn
      
      # update variables
      globalvars.me.turning = 0
      globalvars.me.last_nearest = [host, port, dist]
      globalvars.me.best_entity = [-1, -1, -1, -1, [-1, -1]]
      globalvars.me.last_turn = [-1, -1, -1, [-1, -1]]
      globalvars.me.ent_to_connect = []

      # send message
      list = ["FINDNEAREST", globalvars.me.host, str(globalvars.me.network_port), str(globalvars.me.position[0]), str(globalvars.me.position[1])]
      message = encodeMsg(list)
      globalvars.me.socket.sendto(message, (host, port))

      return
    
    else:
      # discard message
      return

  if (globalvars.me.last_nearest[0] == -1) or (dist == globalvars.me.last_nearest[2]):

    # this entity may be the best, init turn
    globalvars.me.turning = 1
    globalvars.me.best = [ id, host, port, dist, posRel]
    globalvars.me.last_turn = [ id, pos, posRel ]
    globalvars.me.ent_to_connect.append([id, host, port, dist])
    
    # send QUERYAROUND message to entity
    list =  ["QUERYAROUND", globalvars.me.ident, globalvars.me.host, str(globalvars.me.network_port), str(globalvars.me.position[0]), str(globalvars.me.position[1]), globalvars.me.best[0],  str(long(globalvars.me.best[3])) ]
    message = encodeMsg(list)
    globalvars.me.socket.sendto(message, (host, port))

#################################################
#                  AROUND                       #
#################################################

def AROUND(msg):
  """ reception of message:AROUND, id, host, port, positionX, positionY"""

  if globalvars.me.connected or not globalvars.me.turning:
    # discard message
    return
  
  # decode message
  try:
    id, host, stringPort, stringPosX, stringPosY = decodeMsg(msg)
  except:
    return
  
  port = int(stringPort)
  pos = [long(stringPosX), long(stringPosY)]
  posRel = relativePosition(pos, globalvars.me.position)

  # Check if turn ends
  if  len(globalvars.me.ent_to_connect) > 2 and ( (id == globalvars.me.best[0]) or ( not inHalfPlane(globalvars.me.best[4], globalvars.me.position, globalvars.me.last_turn[3]) and inHalfPlane(globalvars.me.best[4], globalvars.me.position, posRel) ) ):
    
    # connected
    globalvars.me.connected = 1
    globalvars.ALIVE = 1

    # compute my awareness radius (min distance with neighbors)
    min_dist = globalvars.me.ent_to_connect[0][3]
    for ent in globalvars.me.ent_to_connect[1:]:
      if ent[3] < min_dist :
	min_dist = ent[3]
	
    globalvars.me.updateAR(min_dist)

    # connect with known entities
    for ent in globalvars.me.ent_to_connect:
      print ent[1], ent[2]

      createEntity(ent[0], ent[1], ent[2], globalvars.me.position, 0, 0, 0, "")
    
    print "WELCOME", globalvars.me.pseudo
    
  else:

    # check if entity is not already known
    infos = [ id, host, port, distance(posRel, globalvars.me.position) ]
    if infos not in globalvars.me.ent_to_connect:

      # save informations on this entity
      globalvars.me.last_turn = [id , host, port, posRel]
      globalvars.me.ent_to_connect.append( infos )

      # send a message
      list =  ["QUERYAROUND", globalvars.me.ident, globalvars.me.host, str(globalvars.me.network_port), str(globalvars.me.position[0]), str(globalvars.me.position[1]), str(globalvars.me.best[0]), str(long(globalvars.me.best[3])) ]
      message = encodeMsg(list)
      globalvars.me.socket.sendto(message, (host, port))
