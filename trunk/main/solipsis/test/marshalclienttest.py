import new
import xmlrpclib
import SimpleXMLRPCServer
from testXMLRPCServer import MyObject

import os,sys

searchPath = os.path.dirname(os.path.dirname(sys.path[0]))
sys.path.append(searchPath)
from solipsis.core.controlevent import ControlEvent

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
