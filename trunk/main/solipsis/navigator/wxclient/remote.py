
import os
import urlparse
import twisted.web.xmlrpc as xmlrpc

from solipsis.util import marshal


def discover_proxy():
    """
    Returns a (host, port) tuple if a proxy is found in the
    current machine configuration, (None, None) otherwise.
    """

    host_port = None

    # Un*x et al.
    if 'http_proxy' in os.environ:
        parts = urlparse.urlparse(os.environ['http_proxy'])
        if not parts[0] or parts[0] == 'http':
            host_port = parts[1]

    # Windows
    try:
        import _winreg as winreg
    except ImportError:
        pass
    else:
        try:
            # Try to grab current proxy settings from the registry
            regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                'Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings')
            regval = winreg.QueryValueEx(regkey, 'ProxyServer')
            regkey.Close()
            regval = str(regval[0])
            # Regval can be of two types:
            # - 'myproxy:3128' if one proxy for all protocols
            # - 'ftp=myftpproxy:3128;http=myhttpproxy:3128;...' if several different proxies
            values = regval.split(';')
            if len(values) > 1:
                for s in values:
                    scheme, p = s.split('=')
                    if scheme == 'http':
                        host_port = p
                        break
            else:
                host_port = values[0]

        except Exception, e:
            print str(e)
            pass

    # Split host and port
    if host_port is not None:
        t = host_port.split(':')
        host = t[0]
        try:
            port = int(t[1])
        except:
            port = 80
        return host, port

    return None, None


class ProxiedXMLRPC:
    """
    A Proxy for making remote XML-RPC calls accross an HTTP proxy.

    Pass the URL of the remote XML-RPC server to the constructor,
    as well as the proxy host and port.

    Use proxy.callRemote('foobar', *args) to call remote method
    'foobar' with *args.
    """

    def __init__(self, reactor, url, proxy_host, proxy_port):
        self.reactor = reactor
        self.url = url
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        parts = urlparse.urlparse(url)
        self.remote_host = parts[1]
        self.secure = parts[0] == 'https'

    def callRemote(self, method, *args):
        factory = xmlrpc.QueryFactory(self.url, self.remote_host, method, *args)
        if self.secure:
            from twisted.internet import ssl
            self.reactor.connectSSL(self.proxy_host, self.proxy_port,
                               factory, ssl.ClientContextFactory())
        else:
            self.reactor.connectTCP(self.proxy_host, self.proxy_port, factory)
        return factory.deferred


class RemoteConnector(object):
    """
    RemoteConnector builds the socket-based connection to the Solipsis node.
    It sends and receives data from the node through an XMLRPC connection.
    """
    def __init__(self, reactor, ui):
        self.reactor = reactor
        self.ui = ui
        self.xmlrpc_control = None
        self.connect_id = None

    def Connect(self, host, port):
        """
        Connect to the node.
        """
        control_url = 'http://%s:%d/RPC2' % (host, port)
        proxy_host, proxy_port = discover_proxy()
        if proxy_host is not None:
            print "HTTP proxy is (%s, %d)" % (proxy_host, proxy_port)
            xmlrpc_control = ProxiedXMLRPC(self.reactor, control_url, proxy_host, proxy_port)
        else:
            print "no HTTP proxy"
            xmlrpc_control = xmlrpc.Proxy(control_url)

        def _success(connect_id):
            # As soon as we are connected, get all peers and ask for events
            self.xmlrpc_control = xmlrpc_control
            self.connect_id = connect_id
            print "connect_id:", connect_id
            self.Call('GetNodeInfo')
            self.Call('GetStatus')
            self.Call('GetAllPeers')
            self._AskEvents()
        def _failure(error):
            print "connection failure:", str(error)
        xmlrpc_control.callRemote('Connect').addCallbacks(_success, _failure)

    def Disconnect(self):
        """
        Disconnect from the node.
        """
        self.Call('Disconnect')
        self.xmlrpc_control = None
        self.connect_id = None

    def Connected(self):
        """
        Returns True if connected.
        """
        return self.xmlrpc_control is not None

    def Call(self, method, *args):
        """
        Call a remote function on the node.
        """
        if self.xmlrpc_control is not None:
            d = self.xmlrpc_control.callRemote(method, self.connect_id, *args)
            _success = getattr(self, "success_" + method, self.success_default)
            _failure = getattr(self, "failure_" + method, self.failure_default)
            d.addCallbacks(_success, _failure)

    #
    # XML RPC callbacks
    #
    def success_default(self, reply):
        pass

    def failure_default(self, error):
        print "failure:", str(error)

    def success_GetAllPeers(self, reply):
        """
        Transmit all peer information to the viewport.
        """
        self.ui.ResetWorld()
        for struct in reply:
            peer_info = marshal.PeerInfo(struct)
            print "PEER", peer_info.id_
            self.ui.AddPeer(peer_info)
        self.ui.Redraw()

    def success_GetEvents(self, reply):
        """
        Process events, then ask for more.
        """
        for notif in reply:
            t, request, payload = notif
            try:
                attr = getattr(self, 'event_' + request)
            except:
                print "Unrecognized notification '%s'" % request
            else:
                attr(payload)
        self._AskEvents()

    def success_GetNodeInfo(self, reply):
        """
        Transmit node information to the viewport.
        """
        node_info = marshal.PeerInfo(reply)
        print "NODE", node_info.id_
        self.ui.UpdateNode(node_info)

    def success_GetStatus(self, reply):
        """
        Trigger visual feedback of the connection status.
        """
        print "STATUS", reply
        self.ui.SetStatus(reply)

    #
    # Notification handlers
    #
    def event_CHANGED(self, struct):
        peer_info = marshal.PeerInfo(struct)
        print "CHANGED", peer_info.id_
        self.ui.UpdatePeer(peer_info)
        self.ui.AskRedraw()

    def event_NEW(self, struct):
        peer_info = marshal.PeerInfo(struct)
        print "NEW", peer_info.id_
        self.ui.AddPeer(peer_info)
        self.ui.AskRedraw()

    def event_LOST(self, peer_id):
        print "LOST", peer_id
        self.ui.RemovePeer(peer_id)
        self.ui.AskRedraw()

    def event_STATUS(self, status):
        print "STATUS", status
        self.ui.SetStatus(status)

    #
    # Private methods
    #
    def _AskEvents(self):
        self.Call('GetEvents')

