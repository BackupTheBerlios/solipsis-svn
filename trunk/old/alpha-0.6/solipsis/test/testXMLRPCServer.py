import xmlrpclib
import SimpleXMLRPCServer

class MyObject:
    def __init__(self,name, id):
        self._name=name
        self._id = id
        self.args = { 'position': '1545 - 56', 'caliber' : 13}
        self.list = ['aliop', 2, 'tytyt']
    def getName(self):
        return self._name

    def getId(self):
        return self._id
    
def getNodeInfo(id):
    print "received id:" + str(id)
    obj = MyObject('testname', id)
    return obj


if __name__ == "__main__":
    server =  SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", 8777))
    server.register_function(getNodeInfo)

    server.handle_request()
