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
Structure of the XML format used for storage:

<entities>
    <entity id="6010_0_6a74d073598e2c07b4ad49411b0fc3a6de0848a3">
        <address>192.34.56.70:6020</address>
        <version>1.1</version>
        <history>
            <connected>1124937580-1125137580</connected>
            <connected>1126165621-1126183604</connected>
        </history>
    </entity>
    <entity id="5800_0_76e546a71b51546c598b95901097115f44c232e8">
        ...
    </entity>
</entities>

"""

from peer import Peer

class EntityCache(object):
    def __init__(self):
        self.history = {}
        self.current_peers = {}

