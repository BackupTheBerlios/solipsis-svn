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

    def __init__(self, id_="", position=Position(), awareness_radius=0,
                 pseudo=u'', address=None):
        """
        Create a new Entity and keep information about it.
        """
        # position
        self.position = position
        self.awareness_radius = awareness_radius

        # public address of this node, address= IP+port
        self.address = address

        # id of this node
        self.id_ = id_

        # Metadata
        self.pseudo = pseudo
        self.services = {}
        self.AddService(Service('chat'))
        self.AddService(Service('video'))
        self.AddService(Service('browse', 'in'))
        self.AddService(Service('share', 'out'))

    def AddService(self, service):
        """
        Add a new service to this entity.
        """
        self.services[service.id_] = service

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

    def Update(self, other):
        """
        Update basic characteristics (not metadata) from the 'other' entity object.
        """
        self.position = other.position
        self.awareness_radius = other.awareness_radius

    def UpdateMeta(self, pseudo=None, services=None):
        """
        Update metadata.
        """
        if pseudo is not None:
            self.pseudo = pseudo
        if services is not None:
            self.UpdateServices(services)

    def UpdateServices(self, new_services):
        """
        Update the entity's services with the new service list.
        """
        self.services.clear()
        for service in new_services:
            self.services[service.id_] = service
    
    def MatchServices(self, entity):
        """
        Match the entity's services with another entity's services.
        Returns the list of the other entity's services that are of interest
        to this entity.
        """
        matched = []
        for service in entity.services:
            # For each offered service, see if it matches ours
            my_service = self.services.get(service.id_)
            if my_service is not None:
                if (service.type, my_service.type) in self.service_matches:
                    matched.append(service)
        return matched

    def __str__(self):
        ent = 'Id:' + str(self.id_) + '\n'
        ent += 'Position:' +  str(self.position)+ '\n'
        ent += 'ar:' + str(self.awareness_radius)+ '\n'
        ent += 'Pseudo:' + str(self.pseudo)   + '\n'
        ent += 'Address:' + str(self.address)+ '\n'
        return ent
