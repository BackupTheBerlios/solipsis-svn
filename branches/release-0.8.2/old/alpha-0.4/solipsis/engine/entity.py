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


class Entity:

    def __init__(self, pos, ori, awarenessRadius, calibre, pseudo):
        """ Create a new Entity and keep information about it"""

        # position and relative position
        self.position = [long(pos[0]), long(pos[1])]
        
        # awareness radius, caliber, pseudo, orientation
        self.awarenessRadius = awarenessRadius
        self.calibre         = calibre
        self.pseudo          = pseudo
        self.orientation     = ori

        # public address of this node, address= IP+port
        self.host = ""
        self.port = 0
        
        # id of this node
        self.id = ""

    def createId(self):
        """ Compute the new ID of this node """
        id = str(self.host) + ":" + str(self.port)
        self.id = id
        return id

    def setId(self, ID):
        self.id = ID

    def getId(self):
        """ Get the ID of this node """
        return self.id

    def getAddress(self):
        return str(self.host) + ":" + str(self.port)

    def getStringPosition(self):
        return str(self.position[0]) + " - " + str(self.position[1])

    def getAwarenessRadius(self):
        return self.awarenessRadius

    def getCalibre(self):
        return self.calibre

    def getOrientation(self):
        return self.orientation
    
    def getPseudo(self):
        return self.pseudo
    
    def getNetAddress(self):
        """ Get the network address of this node
        The network address is a list [ host, port]
        """
        return [ self.host, self.port]

    def updateAr(self, newAr):
        """ update the awareness radius of the entity
        newAr: the new value for the awareness radius
        """
        self.awarenessRadius = newAr

    def getAllInfo(self):
        """ return all information available for this node
        """
        return [ self.id, self.host, str(self.port), str(self.position[0]),
                 str(self.position[1]), str(self.awarenessRadius),
                 str(self.caliber), self.pseudo, str(self.orientation)]

    def getConnectInfo(self):
        return [ self.host, str(self.port), str(self.position[0]),
                 str(self.position[1])]

    def setOrientation(self, value):
        self.orientation = value

    def setAwarenessRadius(self, value):
        self.awarnessRadius = value
