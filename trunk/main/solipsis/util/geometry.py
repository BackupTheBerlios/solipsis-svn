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
import math

class Position(object):
    """ Represents a Solipsis position. """

    SEPARATOR = ','

    def __init__(self, posX=0, posY=0, posZ=0, strPosition=''):
        """ Constructor.
        posX : coordinate on the X axis
        posY : coordinate on the Y axis
        strPosition : position in string format
        """
        if strPosition <> '':
            self.setValueFromString(strPosition)
        else:
            self.posX = long(posX)
            self.posY = long(posY)
            self.posZ = long(posZ)

    def getCoords(self):
        return (self.posX, self.posY)

    def getPosX(self):
        return self.posX

    def getPosY(self):
        return self.posY

    def getPosZ(self):
        return self.posZ

    def setPosX(self, newPosX):
        self.posX = newPosX

    def setPosY(self, newPosY):
        self.posY = newPosY

    def setPosZ(self, newPosZ):
        self.posZ = newPosZ

    def toString(self):
        """ String representation of the position"""
        return str(self.posX) + " " + Position.SEPARATOR + " " + str(self.posY) \
               + " " + Position.SEPARATOR + " " + str(self.posZ)


    def setValueFromString(self, strPosition):
        """ Set the new coordinates of this Position object.
        strPosition: a string representing the position '12454568745 - 7897456'
        """
        coords = strPosition.split(Position.SEPARATOR)
        assert len(coords) == 3, "Wrong string '%s' for Position" % strPosition
        try:
            self.posX = long(coords[0])
            self.posY = long(coords[1])
            self.posZ = long(coords[2])
        except:
            raise Exception("Wrong string '%s' for Position" % strPosition)

    def __eq__(self, other):
        """ Equality operator, used to check if Postion1 == Position2"""
        return ( self.getPosX() == other.getPosX()) and \
               ( self.getPosY() == other.getPosY()) and \
               ( self.getPosZ() == other.getPosZ())

    def __str__(self):
        return self.toString()


class Geometry(object):
    # size should be initialized before class is used
    SIZE = 0

    def distance(p1, p2):
        """ compute euclidean distance for the minimal geodesic between two
        positions p1 and p2
        Static method.
        """
        rp1 = Geometry.relativePosition(p1, p2)
        return long ( math.hypot( rp1.getPosX()-p2.getPosX(),
                                  rp1.getPosY()-p2.getPosY() ) )

    def relativePosition(pos, ref):
        """ Return the relative position of pos (relative to ref)
        Static method.
        Internal method only used by Geometry module, since the relative position
        can be outside the coordinate system
        E.g. If SIZE = 20 (coordinates from (-10,-10) to (10,10)),
        the point (9,1) is close to point (-9, 1): the distance between
        these points is 2.
        relative position of (9,1) is then (-11,1)
        pos : a Position object
        ref : a Position object
        """

        result = Position(pos.getPosX(), pos.getPosY())
        size = Geometry.SIZE
        half_size = long(size / 2)

        #-----Step 1: x-axis

        if pos.getPosX() > ref.getPosX():
            if pos.getPosX() - ref.getPosX() > half_size:
                result.setPosX(pos.getPosX() - size)
        else:
            if ref.getPosX() - pos.getPosX() > half_size:
                result.setPosX(pos.getPosX() + size)

        #-----Step 2: y-axis

        if pos.getPosY() > ref.getPosY():
            if pos.getPosY() - ref.getPosY() > half_size:
                result.setPosY(pos.getPosY() - size)
        else:
            if ref.getPosY() - pos.getPosY() > half_size:
                result.setPosY(pos.getPosY() + size)

        return result


    def localPosition(peerPosition, origin):
        """ Return the new coordinate of a point, using a new origin.
        Used to compute the coordinate of a peer in the coordinate system centered
        around the node: in this system the node has coordinate [0,0]
        peerPosition: old coordinate of point
        origin: new origin for the new coordinate system """
        # compute relative position of these two points
        relativePeerPosition = Geometry.relativePosition(peerPosition, origin)

        return Position(relativePeerPosition.getPosX() - origin.getPosX(),
                relativePeerPosition.getPosY() - origin.getPosY())

    def inHalfPlane(p1, p2, pos):
        """ TRUE if (pos,p1,p2) is a positive angle

        compute if pos belongs to half-plane delimited by (p1, p2)
        p2 is the central point for ccw
        return boolean TRUE if pos belongs to half-plane"""
        rp1  = Geometry.relativePosition(p1,p2)
        rpos = Geometry.relativePosition(pos, p2)
        return (rpos.getPosX()-rp1.getPosX())*(rp1.getPosY()-p2.getPosY()) + \
               (rpos.getPosY()-rp1.getPosY())*(p2.getPosX()-rp1.getPosX()) > 0

    def ccwOrder(x, y):
        """ return TRUE if entity y is before entity x in ccw order relation
        to position of the node (coordinate [0,0] using local position"""

        # take the p-relative position of x and y
        xx = x.localPosition
        yy = y.localPosition

        # verify that they lie in the same half-plane (up or down to pos)
        upX = xx.getPosY() <= 0
        upY = yy.getPosY() <= 0

        if upX <> upY:
            # they do not lie to the same half-plane, y is before x if y is up
            result = upY
        else:
            # they lie in the same plane, compute the determinant and check the sign
            result = not Geometry.inHalfPlane(xx, Position(0,0), yy)

        return result

    def distOrder(x, y):
        """ return TRUE if entity y is closer to the node than entity x
        Node is at coordinate [0,0]
        """

        xx = x.localPosition
        yy = y.localPosition

        return ( Geometry.distance(yy, Position(0,0)) <
                 Geometry.distance(xx, Position(0,0)) )

    distance = staticmethod(distance)
    relativePosition = staticmethod(relativePosition)
    localPosition = staticmethod(localPosition)
    inHalfPlane = staticmethod(inHalfPlane)
    ccwOrder = staticmethod(ccwOrder)
    distOrder = staticmethod(distOrder)

