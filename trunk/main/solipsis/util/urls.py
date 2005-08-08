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

import re

from solipsis.util.address import Address


class SolipsisURL(object):
    """
    Represents a Solipsis URL.
    Can be created from strings of the form 'slp://123.45.67.89:9900/'.
    """

    url_pattern = r'^slp://(\d+\.\d+\.\d+\.\d+):(\d+)/?$'
    url_regexp = re.compile(url_pattern)

    def __init__(self, host, port):
        self.host, self.port = host, port

    def FromString(cls, s):
        m = cls.url_regexp.match(s)
        if m is not None:
            host = m.group(1)
            port = m.group(2)
            return cls(host, port)
        else:
            raise ValueError("Bad Solipsis URL: '%s'" % s)

    FromString = classmethod(FromString)

    def ToString(self):
        return "slp://%s:%d" % (self.host, self.port)

    def GetAddress(self):
        return Address(host=self.host, port=self.port)
