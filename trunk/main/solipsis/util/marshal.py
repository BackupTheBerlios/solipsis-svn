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


from solipsis.util.address import Address


class Marshallable:
    """
    Marshallable is the base class for classes that are to be marshallable
    by simple protocols like XMLRPC. It means Marshallable objects can be
    converted to/from a dictionnary (which can be nested).
    """

    def __init__(self, struct=None):
        """
        Create a Marshallable from struct (dictionnary).
        """
        if struct is None:
            for name, (default, cons) in self.fields.iteritems():
                setattr(self, name, default)
        else:
            for name, (default, cons) in self.fields.iteritems():
                setattr(self, name, cons(struct[name]))

    def ToStruct(self):
        """
        Return struct (dictionnary) from Marshallable.
        """
        d = {}
        for k, v in self.__dict__.iteritems():
            assert v is not None, "Cannot marshal None!"
            if isinstance(v, Marshallable):
                d[k] = v.ToStruct()
            elif isinstance(v, list):
                d[k] = [w.ToStruct() for w in v]
            else:
                d[k] = v
        #~ print d
        return d


class ServiceInfo(Marshallable):
    fields = {
        'id_':
            ("", str),
        'type':
            ("bidir", str),
        'address':
            ("", str),
    }
    
    def FromService(self, service):
        self.id_ = service.id_
        self.type = service.type
        self.address = service.address


class PeerInfo(Marshallable):
    """
    This is a container class used to send node information to/from a navigator.
    """
    fields = {
        'id_':
            ("", str),
        'pseudo':
            (u"", unicode),
        'address':
            ("", lambda a: Address(strAddress=a)),
        'awareness_radius':
            (0.0, float),
        'position':
            ((0.0, 0.0, 0.0), lambda p: map(float, p)),
        'services':
            ([], lambda l: [ServiceInfo(s) for s in l]),
    }

    def FromPeer(self, peer):
        """
        Fill PeerInfo from peer.
        """
        self.id_ = peer.id_
        x, y = peer.position.getCoords()
        self.position = (float(x), float(y), float(peer.position.getPosZ()))
        self.pseudo = unicode(peer.pseudo)
        self.address = peer.address.toString()
        self.awareness_radius = float(peer.awareness_radius)
        self.services = []
        for s in peer.GetServices():
            service = ServiceInfo()
            service.FromService(s)
            self.services.append(service)
