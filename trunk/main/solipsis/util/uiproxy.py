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

import wx
import wx.lib.newevent

#~ UIProxyEvent, EVT_PROXY = wx.lib.newevent.NewEvent()

class TwistedProxy(object):
    """ This is a Twisted proxy. Delegate method calls to this object and
    they will be executed by the Twisted event loop in its own thread. """

    def __init__(self, realobj, reactor):
        self._target = realobj
        self.reactor = reactor
        self.enabled = True

    def __getattr__(self, name):
        print "proxying network __getattr__", name
        attr = getattr(self._target, name)
        call = self.reactor.callFromThread
        if callable(attr):
            # This is the real proxy method we generate on-the-fly
            def fun(*args, **kargs):
                if self.enabled:
                    call(attr, *args, **kargs)
                else:
                    print "TwistedProxy disabled, event discarded"
            setattr(self, name, fun)
            return fun
        raise AttributeError("can only proxy object methods")

    def DisableProxy(self):
        self.enabled = False


class UIProxy(object):
    """ This is a wxWidgets proxy. Delegate method calls to this object and
    they will be executed from the wxWidgets event loop in its own thread.

    For this to work you will also have to make your wx.App class inherit
    from the UIProxyReceiver mix-in (it will define the event handler for
    custom proxy events). """

    def __init__(self, realobj):
        if not isinstance(realobj, wx.EvtHandler):
            raise TypeError(`type(realobj)` + " is not a subclass of wxEvtHandler")
        self._target = realobj
        self._methods = {}

    def __getattr__(self, name):
        print "proxying UI __getattr__", name
        attr = getattr(self._target, name)
        ProxyEvent = self._target._ProxyEvent
        if callable(attr):
            def fun(*args, **kargs):
                evt = ProxyEvent(method = lambda: attr(*args, **kargs))
                wx.PostEvent(self._target, evt)
            setattr(self, name, fun)
            return fun
        raise AttributeError("can only proxy object methods")


class UIProxyReceiver(object):
    def __init__(self):
        self._ProxyEvent, EVT_PROXY = wx.lib.newevent.NewEvent()
        self._enabled = True
        self.Bind(EVT_PROXY, self._DoProxyEvent)

    def _DoProxyEvent(self, event):
        if self._enabled:
            event.method()
        else:
            print "UIProxy disabled, event discarded"
    
    def DisableProxy(self):
        self._enabled = False
