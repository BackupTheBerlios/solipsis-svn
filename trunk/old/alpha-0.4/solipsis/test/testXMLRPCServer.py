import xmlrpclib
import SimpleXMLRPCServer

def getNodeInfo(id):
    print "recived id:" + str(id)
    return ['unknown', '10.193.167.18', '0', '4', '1', '1', '1024',
            'anonymous_23857', '0']


server =  SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", 8777))
server.register_function(getNodeInfo)

server.handle_request()
