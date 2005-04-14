import xmlrpclib
import SimpleXMLRPCServer

server = xmlrpclib.ServerProxy("http://localhost:8777")
id=55
node = server.getNodeInfo(id)
print node
