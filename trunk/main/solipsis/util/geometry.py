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


class Position(object):
    """
    Represents a Solipsis position.
    """
    def __init__(self, (x, y, z) = (0, 0, 0)):
        self.x = x
        self.y = y
        self.z = z

    def GetXY(self):
        return (self.x, self.y)

    def GetXYZ(self):
        return (self.x, self.y, self.z)

    def ToString(self):
        """
        String representation of the position.
        """
        return ", ".join((self.x, self.y, self.z))

    def FromString(cls, s):
        """
        Create a new Position from a string.
        """
        coords = s.split(',')
        assert len(coords) == 3, "Wrong string '%s' for Position" % s
        obj = cls()
        try:
            obj.x = long(coords[0])
            obj.y = long(coords[1])
            obj.z = long(coords[2])
        except:
            raise Exception("Wrong string '%s' for Position" % s)
    
    FromString = classmethod(FromString)
