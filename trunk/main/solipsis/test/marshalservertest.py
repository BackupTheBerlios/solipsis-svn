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
