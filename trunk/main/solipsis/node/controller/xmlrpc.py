
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
        control_section = {
            'host': ('xmlrpc_host', str, ""),
            'port': ('xmlrpc_port', int, 8550),
        }
        self.params.LoadSection('controller_xmlrpc', control_section)

    def Start(self, pool_num):
        """
        Start listening to XML-RPC requests.
        """
        self.listening = self.reactor.listenTCP(pool_num + self.params.xmlrpc_port,
            server.Site(self, timeout=30), interface=self.params.xmlrpc_host)

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

