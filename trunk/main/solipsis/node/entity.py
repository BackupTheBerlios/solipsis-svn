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

try:
    set
except:
    from sets import Set as set

from solipsis.util.geometry import Position


class Service(object):
    def __init__(self, id_, type='bidir'):
        assert type in ('in', 'out', 'bidir'), "Wrong service type"
        self.id_ = id_
        self.type = type


class Entity(object):
    """
    An entity is a participant is the Solipsis world. It conforms to the
    Solipsis protocol, maintaining a number of properties useful to the
    global coherency of the world.
    """

    service_matches = set([
        ('in', 'out'),
        ('in', 'bidir'),
        ('out', 'in'),
        ('out', 'bidir'),
        ('bidir', 'in'),
        ('bidir', 'out'),
        ('bidir', 'bidir'),
    ])

    def __init__(self, id_="", position=Position(), orientation=0, awareness_radius=0,
                 calibre=0, pseudo=u'', address=None):
        """
        Create a new Entity and keep information about it.
        """
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
        self.AddService('chat')
        self.AddService('video')
        self.AddService('browse', 'in')
        self.AddService('share', 'out')

    def AddService(self, service):
        """
        Add a new service to this entity.
        """
        d[service.id_] = service

    def RemoveService(self, service_id):
        """
        Remove a service.
        """
        if service_id in self.services:
            del(self.services[service_id])

    def GetServices(self):
        """
        Get a list of the entity's services.
        """
        return self.services.values()

    def UpdateServices(self, services):
        """
        Update the entity's services with the new service list.
        """
        self.services.clear()
        for service in services:
            self.services[service.service_id] = service
    
    def MatchServices(self, entity):
        """
        Match the entity's services with another entity's services.
        Returns the list of the other entity's services that are of interest
        to this entity.
        """
        matched = []
        for service in entity.services:
            my_service = self.services.get(service.id_)
            if my_service is not None:
                if (service.type, my_service.type) in self.service_matches:
                    matched.append(service)
        return matched

    def __str__(self):
        ent = 'Id:' + str(self.id_) + '\n'
        ent += 'Position:' +  str(self.position)+ '\n'
        ent += 'ar:' + str(self.awareness_radius)+ '\n'
        ent += 'Calibre:' + str(self.calibre)     + '\n'
        ent += 'Pseudo:' + str(self.pseudo)   + '\n'
        ent += 'Orientation:' + str(self.orientation)    + '\n'
        ent += 'Address:' + str(self.address)+ '\n'
        return ent
