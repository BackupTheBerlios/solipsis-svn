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
class Service(object):
    ID_UNKNOWN = 0
    ID_CHAT = 1
    ID_FILE_TRANSFER = 2
    ID_AVATAR = 3

    def __init__(self, id, desc, address):
        """ Constructor.
        id : a string representing the id of the service
        desc : the description of the service
        address: a string describing how to connect to the service
        e.g. '192.168.10.2:8977'
        """
        self.id = id
        self.desc = desc
        self.address = address
        self.isStopping = False
        self.outgoing = NotificationQueue()

    def getId(self):
        return self.id

    def getDescription(self):
        return self.desc

    def getAddress(self):
        return self.address

    def stop(self):
        """ stop the service """
        self.isStopping = True
