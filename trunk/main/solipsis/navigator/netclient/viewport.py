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

from solipsis.navigator.viewport import BaseViewport

def _pretty_pos((x, y)):
    """returns pretty formated position"""
    return "%f,%f"% (x/float(2**128), y/float(2**128))

class Viewport(BaseViewport):

    def __init__(self, world_size = 2**128):
        BaseViewport.__init__(self, world_size)
        self.disabled = True
 
    def Draw(self, onPaint = False):
        pass

    def JumpTo(self, position):
        pass

    def MoveTo(self, position):
        pass
        
    def MoveObject(self, name, position):
        """
        Move an existing object in the viewport.
        """
        try:
            index = BaseViewport.MoveObject(self, name, position)
            self.positions[index] = position
        except KeyError:
            print "Cannot move unknown object '%s' in viewport" % name
            return

