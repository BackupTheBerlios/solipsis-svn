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

from solipsis.util.marshal import Marshallable
from solipsis.util.autohash import Autohash


class Address(Marshallable):
    """
    Represents a Solipsis Address.
    """
    __metaclass__ = Autohash(('host', 'port'))

    marshallable_fields = {
        'host':
            ("", str),
        'port':
            (0, int),
    }

    def __init__(self, host="", port=0):
        """
        Create a new Address object from hostname, port number.
        """
        self.host = str(host)
        self.port = int(port)

    def ToString(self):
        return "%s:%d" % (self.host, self.port)

    def FromString(cls, s):
        t = s.split(':')
        if len(t) != 2:
            raise ValueError("Wrong address format: '%s'" % s)
        obj = cls(t[0].strip(), t[1])
        return obj

    FromString = classmethod(FromString)

    def GetURL(self):
        from solipsis.util.urls import SolipsisURL
        return SolipsisURL(host=self.host, port=self.port)

    def __eq__(self, other):
        return self.host == other.host and self.port == other.port

    def __ne__(self, other):
        return self.host != other.host or self.port != other.port

