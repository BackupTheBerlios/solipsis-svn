
import wx
import wx.lib.newevent

UIProxyEvent, EVT_PROXY = wx.lib.newevent.NewEvent()

class TwistedProxy(object):
    """ This is a Twisted proxy. Delegate method calls to this object and
    they will be executed from the Twisted event loop in its own thread. """

    def __init__(self, realobj, reactor):
        self._target = realobj
        self.reactor = reactor

    def __getattr__(self, name):
        print "proxying daemon __getattr__"
        attr = self._target.__getattribute__(name)
        call = self.reactor.callFromThread
        if callable(attr):
            def fun(*args, **kargs):
                call(attr, *args, **kargs)
            self.__setattr__(name, fun)
            return fun
        raise AttributeError("can only proxy object methods")


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
        print "proxying UI __getattr__"
        attr = self._target.__getattribute__(name)
        if callable(attr):
            def fun(*args, **kargs):
                evt = UIProxyEvent(method = lambda: attr(*args, **kargs))
                wx.PostEvent(self._target, evt)
            self.__setattr__(name, fun)
            return fun
        raise AttributeError("can only proxy object methods")


class UIProxyReceiver(object):
    def __init__(self):
        self.enabled = True
        self.Bind(EVT_PROXY, self.DoProxyEvent)

    def DoProxyEvent(self, event):
        if self.enabled:
            event.method()
        else:
            print "Proxy disabled, event discarded"

    def DisableProxy(self):
        self.enabled = False
