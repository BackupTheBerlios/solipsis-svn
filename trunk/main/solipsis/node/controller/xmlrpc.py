
from twisted.web import xmlrpc, server

class Controller(xmlrpc.XMLRPC):
    """
    This Controller acts as an XML RPC request receiver.
    It forwards these requests to a RemoteControl object.
    """
    method_prefix = 'xmlrpc_'

    def __init__(self, reactor, params, remote_control):
        xmlrpc.XMLRPC.__init__(self)
        self.reactor = reactor
        self.params = params
        self.remote_control = remote_control

    def Start(self, pool_num=0):
        """
        Start listening to XML-RPC requests.
        """
        self.listening = self.reactor.listenTCP(self.params.control_port + pool_num, server.Site(self))

    def Stop(self):
        """
        Stop listening.
        """
        self.listening.stopListening()

    def __getattr__(self, name):
        # Dispatch an RPC to the real connector
        if name.startswith(self.method_prefix):
            realname = 'remote_' + name[len(self.method_prefix):]
            print "proxying %s" % realname
            fun = getattr(self.remote_control, realname)
            setattr(self, name, fun)
            return fun
        raise AttributeError("XMLRPCListener.%s" % name)

