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
import new
import xmlrpclib
import SimpleXMLRPCServer
from testXMLRPCServer import MyObject

import os,sys

searchPath = os.path.dirname(os.path.dirname(sys.path[0]))
sys.path.append(searchPath)
from solipsis.node.controlevent import ControlEvent

def getmyobj():
    id=55
    objDict = server.getMyObject(id)
    obj = new.instance(MyObject, objDict)
    print obj


if len(sys.argv) > 1:
    port = int(sys.argv[1])
else: port = 8777

server = xmlrpclib.ServerProxy("http://localhost:"+ str(port))

getmyobj()
#controlevent = server.getControlEvent()
