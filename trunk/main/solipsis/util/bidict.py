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
"""
A bi-directional dictionary.
It functions like a normal dictionary, except that it also
builds a reverse mapping from values to keys.

To access the reverse mapping, just use the get_reverse() method
instead of the traditionnal get() method.

Warning: only simple access methods are implemented.
Don't try to use other methods than d[] = '...' to modify the
dictionary, otherwise the reverse mapping will be out of sync.

"""

class bidict(dict):
    def __init__(self):
        super(bidict, self).__init__()
        self._rev = {}

    def __setitem__(self, key, value):
        super(bidict, self).__setitem__(key, value)
        self._rev[value] = key

    def __delitem__(self, key):
        value = self[key]
        super(bidict, self).__delitem__(key)
        del self._rev[value]

    def get_reverse(self, value, default=None):
        """ Get the key corresponding to the given value. """
        return self._rev.get(value, default)

    def reversed(self):
        return self._rev


