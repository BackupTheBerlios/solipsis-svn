# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>

import os
import re
import urlparse
from urllib2 import urlopen

import twisted.web.xmlrpc as xmlrpc

def discover_http_proxy():
    """
    Returns a (host, port) tuple if an HTTP proxy is found in the
    current machine configuration, (None, None) otherwise.
    
    Note: automatic proxy configuration file (*.pac) handling is braindead.
    """

    def d(x):
        print "#http_proxy", x
    host_port = None
    host = port = None
    pac_url = None

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
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
            # Manual proxy configuration
            if winreg.QueryValueEx(k, 'ProxyEnable')[0]:
                regval = winreg.QueryValueEx(k, 'ProxyServer')
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
            # Automatic proxy configuration
            try:
                regval = winreg.QueryValueEx(k, 'AutoConfigURL')
            except WindowsError:
                pass
            else:
                pac_url = str(regval[0])

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
        mode = client.get_string('/system/proxy/mode')
        if mode == 'auto':
            pac_url = client.get_string('/system/proxy/autoconfig_url')
        elif mode == 'manual':
            if client.get_bool('/system/http_proxy/use_http_proxy'):
                host = client.get_string('/system/http_proxy/host')
                port = client.get_int('/system/http_proxy/port')

    # Read PAC file if necessary
    # Yes, we could use Twisted, but we don't need asynchronicity here
    if pac_url and not host and not host_port:
        try:
            f = urlopen(pac_url)
        except Exception, e:
            print str(e)
            pass
        else:
            print pac_url
            # A hack until someone embeds a Javascript interpreter in Python...
            regex = re.compile(r'PROXY\s(\d+.\d+.\d+.\d+:\d+)')
            for l in f:
                m = regex.search(l)
                if m is not None:
                    host_port = m.group(1)
                    break

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
