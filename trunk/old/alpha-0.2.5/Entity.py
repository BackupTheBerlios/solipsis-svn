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
## -----                           Entity.py                                -----
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

import Function
import globalvars
import sys

#################################################################################################
#                                                                                               #
#			----- Information about an entity ---------				#
#                                                                                               #
#################################################################################################

class Entity:
  
  def __init__(self, id, host, port, pos, ori, awareness_radius, caliber, pseudo):
    """ Create a new Entity and keep information about it"""

    # identifier
    self.id = id

    # network data
    self.host = host
    self.port = int(port)

    # position and relative position
    self.position = pos
    relative_position = Function.relativePosition(self.position, globalvars.me.position)
    self.local_position = [ relative_position[0] - globalvars.me.position[0], relative_position[1] - globalvars.me.position[1] ]

    # awareness radius, caliber, pseudo, orientation
    self.awareness_radius = awareness_radius
    self.caliber = caliber
    self.pseudo = pseudo
    self.ori = ori

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

#################################################
#              addService                       #
#################################################     

  def addService(self, id_service, desc_service, host, port):
    """ add a new service"""

    self.services[id_service] = [desc_service, host, port]

#################################################
#              closeService                     #
#################################################     

  def closeService(self, id_service):
    """ delete service"""

    if self.services.has_key(id_service):
      del self.services[id_service]

#################################################
#              sendNetworkMessage               #
#################################################     

  def sendNetworkMessage(self, msg):
    """ Send a message to this entity"""

    globalvars.me.socket.sendto(msg, (self.host, self.port))

    # update message_sent
    if msg[:5] <> "FOUND" and msg[:7] <> "DETECT":
      globalvars.message_sent = 1
    
#################################################
#              updateOri                        #
#################################################

  def updateOri(self, new_ori):
    """ update entity orientation """
    
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

#################################################
#              updatePos                        #
#################################################
    
  def updatePos(self, new_pos):
    """ update the position of the entity"""
    
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

#################################################
#              updateAr                         #
#################################################

  def updateAr(self, delta_ar):
    """ update the awareness radius of the entity"""
    
    # Nothing special to do.
    self.awareness_radius += delta_ar
    
#################################################
#              confirm                          #
#################################################

  def confirm(self, pos, ori, ar, ca, pseudo):
    """ confirm and update informations: to detect liars"""

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

#################################################
#              updateReference                  #
#################################################

  def updateReference(self):
    """ Set up the position when the local node move."""
    
    # The node is the center of a local bench mark.
    relative_position = Function.relativePosition(self.position, globalvars.me.position)
    self.local_position = [ long(relative_position[0] - globalvars.me.position[0]), long(relative_position[1] - globalvars.me.position[1]) ]
    

