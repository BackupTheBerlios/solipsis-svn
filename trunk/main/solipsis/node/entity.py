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

    def __init__(self, id_="", position=Position(), orientation=0, awareness_radius=0,
                 calibre=0, pseudo='', address=None):
        """ Create a new Entity and keep information about it"""

        # position
        self.position = position

        # awareness radius, calibre, pseudo, orientation
        self.awareness_radius = awareness_radius
        self.calibre = calibre
        self.pseudo = pseudo
        self.orientation = orientation

        # public address of this node, address= IP+port
        self.address = address

        # id of this node
        self.id_ = id_

        self.services = {}

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
        ent = 'Id:' + str(self.id_) + '\n'
        ent += 'Position:' +  str(self.position)+ '\n'
        ent += 'ar:' + str(self.awareness_radius)+ '\n'
        ent += 'Calibre:' + str(self.calibre)     + '\n'
        ent += 'Pseudo:' + str(self.pseudo)   + '\n'
        ent += 'Orientation:' + str(self.orientation)    + '\n'
        ent += 'Address:' + str(self.address)+ '\n'
        return ent
