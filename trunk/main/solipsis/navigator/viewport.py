# pylint: disable-msg=C0103,W0131
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
"""Simple interface for viewports. Those functions are callbacks used
by world.py"""

class BaseViewport(object):

    def __init__(self, world_size=2**128, disable=True):
        self.world_size = world_size
        self.normalize = (lambda x, lim=float(self.world_size) / 2.0: \
                          (x + lim) % (lim + lim) - lim)
        self.disabled = disable

    def Disable(self):
        self.disabled = True

    def Enable(self):
        self.disabled = False

    def Reset(self):
        # (object name -> index) dictionary
        self.obj_dict = {}
        # List of objects
        self.obj_list = []
        self.obj_name = []
        self.obj_visible = []
        # List of dicts of drawables
        self.positions = []
        self.future_positions = []
        self.obj_arrays = (self.obj_list, self.obj_name, self.obj_visible, 
            self.positions, self.future_positions)

    def Draw(self, onPaint = False):
        """refresh the viewport"""
        raise NotImplementedError

    def AddObject(self, name, obj, position):
        """
        Add an object to this viewport.
        """
        # First add the object to the dictionary
        name = intern(name)
        if name in self.obj_dict:
            print "Cannot add already existing object '%s' to viewport" % name
            return self.obj_dict[name]
        index = len(self.obj_list)
        self.obj_dict[name] = index
        for array in self.obj_arrays:
            array.append(None)
        self.obj_list[index] = obj
        # Then initialize the object's properties
        self.obj_name[index] = name
        self.positions[index] = position
        self.future_positions[index] = position, position
        self.obj_visible[index] = True
        return index

    def RemoveObject(self, name):
        """
        Remove an object from this viewport (and all its associated drawables).
        """
        try:
            index = self.obj_dict[name]
        except KeyError:
            print "Cannot remove unknown object '%s' from viewport" % name
            return
        self._RemoveByIndex(index)

    def MoveObject(self, name, position):
        """
        Move an existing object in the viewport.
        """
        try:
            index = self.obj_dict[name]
        except KeyError:
            print "Cannot move unknown object '%s' in viewport" % name
            raise
        self.future_positions[index] = position, self.positions[index]
        return index

    def JumpTo(self, position):
        raise NotImplementedError

    def MoveTo(self, position):
        raise NotImplementedError

    def GetObjectPosition(self, name):
        try:
            index = self.obj_dict[name]
            x, y = self.positions[index]
            return "%f %f"% (float(x)/self.world_size, float(y)/self.world_size)
        except KeyError:
            return "Not valid anymore"
 
    #
    # Private methods: object management
    #

    def _RemoveByIndex(self, index):
        """
        Remove an object giving its index rather than its name.
        """
        # Delete stored object properties
        name = self.obj_name[index]
        for array in self.obj_arrays:
            del array[index]
        del self.obj_dict[name]
        # Re-arrange moved objects in dictionary
        _names = self.obj_name
        for i in xrange(index, len(_names)):
            self.obj_dict[_names[i]] = i
