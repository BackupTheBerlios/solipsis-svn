# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>
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
## ---- entity.py
## ------------------------------------------------------------------------------
from solipsis.util.geometry import Position

class Entity(object):

    def __init__(self, id="", position=Position(), ori=0, awarenessRadius=0,
                 calibre=0, pseudo='', address=None):
        """ Create a new Entity and keep information about it"""

        # position
        self.position = position

        # awareness radius, calibre, pseudo, orientation
        self.awarenessRadius = awarenessRadius
        self.calibre         = calibre
        self.pseudo          = pseudo
        self.orientation     = ori

        # public address of this node, address= IP+port
        self.address = address

        # id of this node
        self.id = id

        self.services = {}

    def setId(self, ID):
        self.id = ID

    def getId(self):
        """ Get the ID of this node """
        return self.id

    def getAddress(self):
        return self.address

    def getStringPosition(self):
        return self.position.toString()

    def getPosition(self):
        return self.position

    def getAwarenessRadius(self):
        return self.awarenessRadius

    def getCalibre(self):
        return self.calibre

    def getOrientation(self):
        return self.orientation

    def getPseudo(self):
        return self.pseudo

    def setOrientation(self, value):
        self.orientation = value

    def setAwarenessRadius(self, value):
        self.awarenessRadius = long(value)

    def setCalibre(self, value):
        self.calibre = value

    def setPseudo(self, value):
        self.pseudo = value

    def setPosition(self, pos):
        """ Set the new position of this entity
        pos : a Position object """
        self.position = pos

    def setAddress(self, newAddress):
        """ newAddress : a Address object"""
        self.address = newAddress

    def enumerateServices(self):
        return self.services.values()

    def addService(self, srv):
        """ add a new service to this entity
        srv : a Service object
        """
        self.services[srv.getId()] = srv

    def delService(self, srvId):
        """ Remove a service
        srvId : ID of the service to remove"""
        del(self.services[srvId])

    def __str__(self):
        ent = 'Id:' + str(self.id) + '\n'
        ent += 'Position:' +  str(self.position)+ '\n'
        ent += 'relativePosition:'+ str(self.relativePosition)+ '\n'
        ent += 'ar:' + str(self.awarenessRadius )+ '\n'
        ent += 'Calibre:' + str(self.calibre)     + '\n'
        ent += 'Pseudo:' + str(self.pseudo)   + '\n'
        ent += 'Orientation:' + str(self.orientation)    + '\n'
        ent += 'Address:' + str(self.address)+ '\n'
        return ent
