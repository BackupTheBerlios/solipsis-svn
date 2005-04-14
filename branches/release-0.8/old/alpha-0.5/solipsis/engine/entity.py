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


from solipsis.navigator.service import Service

    
class Position:
    """ Represents a Solipsis position. """

    SEPARATOR = '-'
    
    def __init__(self, posX=0, posY=0):
        """ Constructor.
        posX : coordinate on the X axis
        posY : coordinate on the Y axis
        """
        self.posX = long(posX)
        self.posY = long(posY)

    def getPosX(self):
        return self.posX

    def getPosY(self):
        return self.posY

    def setPosX(self, newPosX):
        self.posX = newPosX

    def setPosY(self, newPosY):
        self.posY = newPosY
        
    def toString(self):
        """ String representation of the position"""
        return str(self.posX) + " " + Position.SEPARATOR + " " + str(self.posY)

    def setValueFromString(self, strPosition):
        """ Set the new coordinates of this Position object.
        strPosition: a string representing the position '12454568745 - 7897456'
        """
        strPosX, strPosY = strPosition.split(Position.SEPARATOR)
        self.posX = long(strPosX)
        self.posY = long(strPosY)

        
class Address:
    """ Represents a Solipsis Address."""

    SEPARATOR = ':'
    
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

    def toString(self):
        return str(host) + Address.SEPARATOR + str(port)

    def getHost(self):
        return self.host

    def getPort(self):
        return self.port

    def setValueFromString(self, strAddress):
        """ Set the new address of this Address object.
        strAddress: a string representing the address '192.235.22.32:8978'
        """
        strHost, strPort = strAddress.split(Address.SEPARATOR)
        self.host = strHost
        self.port = int(strPort)

class Entity:

    def __init__(self, position=Position(), ori=0, awarenessRadius=0,
                 calibre=0, pseudo=''):
        """ Create a new Entity and keep information about it"""

        # position 
        self.position = position
        # position of this entity in the coordinate system centered on the node
        self.relativePosition = None
        
        # awareness radius, caliber, pseudo, orientation
        self.awarenessRadius = awarenessRadius
        self.calibre         = calibre
        self.pseudo          = pseudo
        self.orientation     = ori

        # public address of this node, address= IP+port
        self.address = None
        
        # id of this node
        self.id = ""

        self.service = {}
        
    def createId(self):
        """ Compute the new ID of this node """
        self.id = self.address.toString()
        return self.id

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

    def getRelativePosition(self):
        return self.relativePosition
    
    def getAwarenessRadius(self):
        return self.awarenessRadius

    def getCalibre(self):
        return self.calibre

    def getOrientation(self):
        return self.orientation
    
    def getPseudo(self):
        return self.pseudo
    

    def updateAr(self, newAr):
        """ update the awareness radius of the entity
        newAr: the new value for the awareness radius
        """
        self.awarenessRadius = newAr

    def getAllInfo(self):
        """ return all information available for this node
        """
        return [ self.id, self.host, str(self.port), str(self.position.getPosX()),
                 str(self.position.getPosY()), str(self.awarenessRadius),
                 str(self.caliber), self.pseudo, str(self.orientation)]

    def getConnectInfo(self):
        return [ self.host, str(self.port), str(self.position.getPosX()),
                 str(self.position.getPosY())]

    def setOrientation(self, value):
        self.orientation = value

    def setAwarenessRadius(self, value):
        self.awarnessRadius = value

    def setCalibre(self, value):
        self.calibre = value

    def setPseudo(self, value):
        self.pseudo = value
        
    def setPosition(self, pos):
        """ Set the new position of this entity
        pos : a Position object """
        self.position = pos

    def setRelativePosition(self, pos):
        """ Set the new position of this entity
        pos : a Position object """
        self.relativePosition = pos

    def setAddress(self, newAddress):
        """ newAddress : a Address object"""
        self.address = newAddress

    def enumerateServices(self):
        return self.service.values()
