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

from autohash import Autohash


class Address(object):
    """
    Represents a Solipsis Address.
    """
    __metaclass__ = Autohash(('host', 'port'))

    SEPARATOR = ':'

    def __init__(self, host='', port=0, strAddress=''):
        """ Constructor. Create a new Address object
        host : host name or IP address
        port : port number
        strAddress : a string representing the network address
        """
        self.host = host
        self.port = int(port)

        # override host, port value if strAddress is not null
        if strAddress <> '':
            self.setValueFromString(strAddress)

    def toString(self):
        return str(self.host) + Address.SEPARATOR + str(self.port)

    def getHost(self):
        return self.host

    def getPort(self):
        return self.port

    def setValueFromString(self, strAddress):
        """ Set the new address of this Address object.
        strAddress: a string representing the address '192.235.22.32:8978'
        """
        if strAddress <> '':
            strHost, strPort = strAddress.split(Address.SEPARATOR)
            if strHost <> '':
                self.host = strHost
            if strPort <> '':
                self.port = int(strPort)

    def __eq__(self, other):
        return ( self.getHost() == other.getHost() ) and \
               ( self.getPort() == other.getPort() )

    def __str__(self):
        return self.toString()

    #~ def __hash__(self):
        #~ return hash(self.host) ^ hash(self.port)
