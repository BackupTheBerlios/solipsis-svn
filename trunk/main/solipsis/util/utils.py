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

import sha
import random

from compat import safe_str


def CreateSecureId(seed=''):
    """
    Creates a new random ID.
    The ID is returned as a hex string.
    (you can optionally specify a seed to improve randomness)
    """
    nbytes = 20
    try:
        r = random.getrandbits(nbytes * 8)
    except AttributeError:
        # Alternate method for Python < 2.4
        r = random.randrange(2 ** (nbytes * 8))
    s = ''
    for i in xrange(nbytes):
        s += chr(r & 0xFF)
        r >>= 8
    s += safe_str(seed)
    return sha.new(s).hexdigest()

class ManagedData(object):
    """
    Derive this class to create Managed data for use with validators.
    Attributes starting with an underscore ('_') will not be managed.
    """
    def __init__(self):
        self._dict = {}

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return
        try:
            self._dict[name][0] = value
        except KeyError:
            self._dict[name] = [value]

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattr__(self, name)
        return self._dict[name][0]

    def GetDict(self):
        """
        Returns a dict containing managed data in an unmanaged way.
        Changes to this dict will not be propagated to the object attributes.
        """
        d = {}
        for k, v in self._dict.iteritems():
            d[k] = v[0]
        return d

    def UpdateDict(self, d):
        """
        Update the attributes with a dictionnary containing values.
        """
        for k, v in d.iteritems():
            if k in self._dict:
                expected_type = type(self._dict[k][0])
                # If the value is not of the attribute's current type,
                # try to convert it
                if expected_type != type(v):
                    try:
                        v = expected_type(v)
                    except Exception, e:
                        print "Could not update attribute '%s' in ManagedData: wrong type '%s'" % (k, type(v).__name__)
                        continue
                self._dict[k][0] = v
            else:
                self._dict[k] = [v]

    def Ref(self, name):
        """
        Returns a reference to an attribute, i.e. the list that contains
        the attribute as sole element.
        """
        return self._dict[name]
