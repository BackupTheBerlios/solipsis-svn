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
## -----                           Self.py                                   -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module defines the class for self informations.
##   It provides the definition of the entity, the methods for the node connection
##   and the methods for the modifications of the variable characteristics.
##
## ******************************************************************************

from socket import socket, AF_INET, SOCK_DGRAM 
import random
import sys
import math

from Function import *
from Entity import Entity
from globalvars import *
from List import CcwList, DistList

class Self_Infos:
  
  def __init__(self, host, network_port, sock, GUI_port, posX, posY, ar, ca, ori, exp, pseudo):
    """ All informations about this node:
    host --> ip if the node, network_port, GUI_port, posX, posY, ar, ca, 
    ori --> a point, 
    exp --> expected number of neighbour, pseudo"""

    #********** Indentier (key) **********.
    self.ident = str(host)+ ":" +str(network_port)

    #********** Network informations **********.
    self.host = host
    self.network_port = int(network_port)
    
    # port GUI
    self.GUI_port = GUI_port
    
    # socket
    self.socket = sock

    #********** Avatar Informations *********
    
    # position, awareness radius, caliber and orientation
    self.position = [posX, posY]
    self.awareness_radius = ar
    self.caliber = ca
    self.ori = ori
    
    # pseudo
    self.pseudo = pseudo
    # maximum expected number of neighbours.
    self.exp = exp

    #********** GUI **********
    
    # variable GuiConnected boolean TRUE if node controlled by a GUI.
    self.GUIConnected = 0
    
    #********** Medias Informations **********
    
    # list of available modules for multimedia communications
    # {id_media: media_object, ...}
    self.media = {}
    
    #********** Neighbors informations **********
    
    # list of adjacents
    self.adjacents = {}
    # ccw ordered list of adjacents
    self.ccwAdjacents = CcwList()
    # distance ordered list of adjacents 
    self.distAdjacents = DistList()

    #********** variables for initialization algorithm **********
    
    # last nearest known entity : host, port, distance
    self.last_nearest = [ -1 , -1, -1]
    # best entity : id, host, port, distance, relative position
    self.best_entity = [-1, -1, -1, -1, [-1, -1]]
    # last known entity for turn : id, host, port, relative position
    self.last_turn = [-1, -1, -1, [-1, -1]]
    # boolean TRUE if turn
    self.turning = 0
    # list of entities for connecion if turn succeeds
    self.ent_to_connect = []
    # booleant TRUE if connected
    self.connected = 0

    #************ dictionnary for met entities ************

    # list {(hostname, port) = 1, ...}
    self.met = {}
    # size of the dictionnary
    self.nb_met = 0

#################################################
#              connection to the world          #
#################################################

  def worldEntrance(self, host = 0, port = 0):
    """ Jump into the world thanks to a known node"""

    self.last_nearest = [ -1 , -1, -1]
    self.best_entity = [-1, -1, -1, -1, [-1, -1]]
    self.last_turn = [-1, -1, -1, [-1, -1]]
    self.turning = 0
    self.ent_to_connect = []
    self.connected = 0

    # message to send
    message = encodeMsg( ["FINDNEAREST", self.host, str(self.network_port), str(self.position[0]), str(self.position[1])] )

    if host:
      # the function is invoked with a special host to contact
      self.socket.sendto(message, (host, int(port)))

    else:

      try:
        f = file('entities.met', 'r')
      except:
        sys.stderr.write("No file for connection...")
        globalvars.ALIVE = 0
        killAllThread()

      # read file
      list = f.readlines()
      
      f.close()
      
      # put randomly 10 entities
      for i in range(10):
        
        # retrieve entity
        entity = random.choice(list)
        host, stringPort = entity.split()
        port = int(stringPort)
        self.socket.sendto(message, (host, port))
      

  def startWorld(self):
    """ Jump into the world thanks to a known node"""
    
    try:
      f = file('entities.met', 'r')
    except:
      sys.stderr.write("Please download a new bootstrap file...")
      sys.exit(0)
      
    # read file
    list = f.readlines()

    # message  
    message = encodeMsg( ["HELLO", self.ident, self.host, str(self.network_port), str(self.position[0]), str(self.position[1]), str(self.awareness_radius), str(self.caliber), self.pseudo, str(self.ori)] )
    
    # put randomly 10 entities
    for i in range(10):

      # retrieve entity
      entity = random.choice(list)
      host, stringPort = string.splitfields(entity)
      port = int(stringPort)

      # create entity
      id = host+":"+stringPort
      new_entity = Entity(id, host, port, [0,0], 0, 0, 0, 'no_pseudo')
      if not self.adjacents.has_key(id):
        self.adjacents[id] = new_entity
        self.distAdjacents.ins(new_entity)
        self.ccwAdjacents.ins(new_entity)

      # send message
      self.socket.sendto(message, (host, port))
      
    f.close()

#################################################
#                updateOri                      #
#################################################  

  def updateOri(self,delta_ori):
    """ update orientation"""

    # retrieve information
    self.ori = int ((self.ori + delta_ori ) % 360)

    # notify orientation to media
    if self.GUIConnected:
      for media in self.media.values():
        if media.push:
          if media.thread.modSelf("ORI", self.ori) == -1:
            sys.stderr.write("error in modSelf ORI")
            if media.addBug():
              del self.media[media.id]
          else:
            media.bug = 0

    # notify orientation to neighbors
    for ent in self.adjacents.values():
      msg = encodeMsg(["DELTA", self.ident, "ORI", str(self.ori)])
      ent.sendNetworkMessage(msg)

#################################################
#                updatePos                      #
#################################################  

  def updatePos(self, dX, dY):
    """ update position """

    old_position = self.position
    string_var = str(dX) + "," + str(dY)

    # notify my mvt to media
    if self.GUIConnected:
      for media in self.media.values():
        if media.push:
          if media.thread.modSelf("POS", string_var) == -1:
            sys.stderr.write("error in modSelf pos")
            if media.addBug():
              del self.media[media.id]
          else:
            media.bug = 0
              
    # update my position
    self.position[0] = long((self.position[0] + dX)% SIZE)
    self.position[1] = long((self.position[1] + dY)% SIZE)
    
    # notify my mvt to neighbors
    string_pos = str(self.position[0]) + ", " + str(self.position[1])
    for ent in self.adjacents.values():
      msg = encodeMsg(["DELTA", self.ident, "POS", string_pos])
      ent.sendNetworkMessage(msg)

      # re-compute new local positions
      ent.updateReference()

    # update list of adjacents
    self.ccwAdjacents.update(self.position)
    self.distAdjacents.update(self.position)
   
    # verify the detection
    self.detectionCheck(old_position)

#################################################
#                updateAr                       #
#################################################

  def updateAR(self, delta_ar):
    """ update AR """
    
    # update my awareness radius
    self.awareness_radius += delta_ar
    stringVar = str(delta_ar)

    # notify to displayers
    if self.GUIConnected:
      for media in self.media.values():
        if media.push:
          if media.thread.modSelf("AR", stringVar) == -1:
            sys.stderr.write("error in modSelf ar")
            if media.addBug():
              del self.media[media.id]
          else:
            media.bug = 0

    # notify to neighbors
    for ent in self.adjacents.values():
      msg = encodeMsg(["DELTA", self.ident, "AR", str(self.awareness_radius)])
      ent.sendNetworkMessage(msg)
      
#################################################
#                detectionCheck                 #
#################################################  

  def detectionCheck(self, old_position):
    """ Verify that self doesn't know an entity nearer to another"""

    listEnt = self.adjacents.values()
    for ent in listEnt:
      i = listEnt.index(ent)
        
      # compute my distances to ent
      myDist = distance([0,0], ent.local_position)
      myOldDist = distance(old_position, relativePosition(ent.position, old_position) )
        
      for ent2 in listEnt[i+1:]:

        # compute their distance
        theirDist = distance(ent2.position, relativePosition(ent.position, ent2.position))

        # compute my distances to ent2
        myDist2 = distance([0,0], ent2.local_position)
	myOldDist2 = distance(old_position, relativePosition(ent2.position, old_position) )

        if myDist > theirDist > myOldDist:
          # ent2 is now closer to ent than self
          # DETECT message sent to ent
          list = ["DETECT", ent2.id, str(ent2.position[0]), str(ent2.position[1]), str(ent2.awareness_radius), str(ent2.caliber), ent2.pseudo]
          message = encodeMsg(list)
          ent.sendNetworkMessage(message)

        if myDist2 > theirDist > myOldDist2:
          # ent is now closer to ent2 than self
          # DETECT message sent to ent2
          list = ["DETECT", ent.id, str(ent.position[0]), str(ent.position[1]), str(ent.awareness_radius), str(ent.caliber), ent.pseudo]
          message = encodeMsg(list)
          ent.sendNetworkMessage(message)

