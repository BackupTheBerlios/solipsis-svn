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
import xmlrpclib
import SimpleXMLRPCServer
import os,sys
searchPath = os.path.dirname(os.path.dirname(sys.path[0]))
sys.path.append(searchPath)

#from solipsis.node.controlevent import ControlEvent
#from solipsis.node.event import Event

class superObj:
    def __init__(self):
        self.isSuper = True
        
class MyObject(object):
    def __init__(self,name, id):        
        self._name=name
        self._id = id
        self.args = { 'position': '1545 - 56', 'caliber' : 13}
        self.list = ['aliop', 2, 'tytyt']
    def getName(self):
        return self._name

    def getId(self):
        return self._id
    
def getMyObject(id):
    print "received id:" + str(id)
    obj = MyObject('testname', id)
    return obj

def getControlEvent():
    #c = ControlEvent('NODEINFO')
    c= Event('NODEINFO')
    return c

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else: port = 8777
    
    server =  SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", port))
    server.register_function(getMyObject)
    server.register_function(getControlEvent)
    server.handle_request()
