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

import twisted.web.xmlrpc as xmlrpc

import solipsis.util.httpproxy as httpproxy


class _BaseNode(object):
    """
    Base class for node proxying objects.
    """

    class _Proxy(object):
        """
        A proxy class whose method calls will be forwarded to the node.
        """
        def __init__(self, node, connect_id):
            # Instantiates a proxy object
            self.node = node
            self.connect_id = connect_id
        def __getattr__(self, name):
            # Forwards method calls to the actual object handling
            # the underlying RPC protocol.
            success_meth = "success_" + name
            failure_meth = "failure_" + name
            assert self.node.receiver is not None
            # Resolve method callbacks
            try:
                _success = getattr(self.node.receiver, success_meth)
            except AttributeError:
                _success = getattr(self.node, success_meth, self.node.success_default)
            try:     
                _failure = getattr(self.node.receiver, failure_meth)
            except AttributeError:
                _failure = getattr(self.node, failure_meth, self.node.failure_default)
            # Create method and attach it to the proxy
            method = self.node._CreateMethod(name, _success, _failure)
            def fun(*args, **kargs):
                if self.connect_id is not None:
                    method(self.connect_id, *args, **kargs)
            setattr(self, name, fun)
            return fun

    def Connect(self, receiver):
        """
        This method must be overriden.
        Connect to the node, taking a "receiver" object for method responses
        as parameter.
        Returns a Deferred that will return:
        - either a Proxy object if the connection has succeeded
        - or an error through its errback if there was a problem.
        """
        raise NotImplementedError

    def Connected(self):
        """
        Returns True if connected.
        """
        return self._proxy is not None

    def Disconnect(self):
        """
        This method must be overriden.
        Disconnect from the node.
        """
        if self.Connected():
            self._proxy.Disconnect()
            self._proxy = None
            self._Disconnected()

    def Quit(self):
        """
        Kill the node.
        """
        if self.Connected():
            self._proxy.Quit()
            self._proxy = None
            self._Disconnected()

    def Reset(self):
        """
        Reset the node.
        """
        if self.Connected():
            self._proxy.Reset()

    def _CreateMethod(self, method_name, success, failure):
        """
        This method must be overriden.
        It creates a method calling method "method_name" on the remote object
        and ties the response to the "success" and "failure" callbacks.
        """
        raise NotImplementedError

    def _CreateProxy(self, connect_id):
        """
        Returns a proxy object when connecting.
        """
        # emb: removing print because of unittests
        #print "connect_id:", connect_id
        self._proxy = self._Proxy(self, connect_id)
        return self._proxy
        
    def _Disconnected(self):
        """
        Called when connection ends. Should be overriden.
        """
        pass

    def _AskEvents(self):
        if self.Connected():
            self._proxy.GetEvents()


class XMLRPCNode(_BaseNode):
    """
    Class for connecting to a node via XMLRPC.
    """
    def __init__(self, reactor, host, port, proxy_host=None, proxy_port=None):
        _BaseNode.__init__(self)
        self.reactor = reactor
        self.host = host
        self.port = port
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.xmlrpc_control = None
        self.receiver = None

    def Connect(self, receiver):
        """
        Connect to the node, taking a "receiver" object for method responses
        as parameter.
        Returns a Deferred that will return:
        - either a Proxy object if the connection has succeeded
        - or an error through its errback if there was a problem.
        """
        self.receiver = receiver
        control_url = 'http://%s:%d/RPC2' % (self.host, self.port)
        if self.proxy_host and self.proxy_port:
            # emb: removing print because of unittests
            #print "HTTP proxy is (%s, %d)" % (self.proxy_host, self.proxy_port)
            xmlrpc_control = httpproxy.ProxiedXMLRPC(self.reactor,
                control_url, self.proxy_host, self.proxy_port)
        else:
            # emb: removing print because of unittests
            #print "no HTTP proxy"
            xmlrpc_control = xmlrpc.Proxy(control_url)

        def _success(connect_id):
            # Called if the connection has succeeded
            self.xmlrpc_control = xmlrpc_control
            return self._CreateProxy(connect_id)
        def _failure(error):
            # Called if the connection has failed
            self.xmlrpc_control = None
            print "connection failure:", str(error)
            return error
        return xmlrpc_control.callRemote('Connect').addCallbacks(_success, _failure)

    def _Disconnected(self):
        self.xmlrpc_control = None

    def _CreateMethod(self, method_name, success, failure):
        def fun(*args, **kargs):
            assert not kargs, "keyword arguments unsupported by XMLRPC: %s" % str(kargs)
            if self.xmlrpc_control is not None:
                d = self.xmlrpc_control.callRemote(method_name, *args)
                d.addCallbacks(success, failure)
        return fun

    #
    # Method response callbacks
    #
    def success_default(self, reply):
        pass

    def failure_default(self, error):
        print "failure:", str(error)

    def success_GetEvents(self, reply):
        """
        Process events, then ask for more.
        """
        for notif in reply:
            t, request, payload = notif
            try:
                attr = getattr(self.receiver, 'event_' + request)
            except:
                print "Unrecognized notification '%s'" % request
            else:
                attr(payload)
        self._AskEvents()
