import new
import xmlrpclib
import SimpleXMLRPCServer
from testXMLRPCServer import MyObject

server = xmlrpclib.ServerProxy("http://localhost:8777")
id=55
objDict = server.getNodeInfo(id)

obj = new.instance(MyObject, objDict)

print obj



