
import os
import urlparse
import twisted.web.xmlrpc as xmlrpc

def discover_http_proxy():
    """
    Returns a (host, port) tuple if an HTTP proxy is found in the
    current machine configuration, (None, None) otherwise.
    
    Note: it currently doesn't handle automatic proxy configuration files (*.pac).
    """

    host_port = None
    host = port = None

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

    # Gnome
    try:
        import gconf
        client = gconf.client_get_default()
    except:
        pass
    else:
        if client.get_bool('/system/http_proxy/use_http_proxy'):
            host = client.get_string('/system/http_proxy/host')
            port = client.get_int('/system/http_proxy/port')

    # Split host and port if necessary
    if host_port and not host:
        t = host_port.split(':')
        host = t[0].strip()
        if host:
            try:
                port = int(t[1])
            except:
                port = 80

    return host, port


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
