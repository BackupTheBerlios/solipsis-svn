
import os
import sys
import wx
import wx.xrc
from wx.xrc import XRCCTRL, XRCID

from wxutils import _
from wxutils import *        # '*' doesn't import '_'
from validators import *
from viewport import Viewport
from world import World
from proxy import TwistedProxy, UIProxyReceiver
from network import NetworkLoop


class ConnectionData(ManagedData):
    def __init__(self, host=None, port=None, pseudo=None):
        super(ConnectionData, self).__init__()
        self.pseudo = ""
        self.host = "localhost"
        self.port = ""
        if pseudo:
            self.pseudo = pseudo
        if host:
            self.host = host
        if port:
            self.port = port



class NavigatorApp(wx.App, XRCLoader, UIProxyReceiver):
    """
    Main application class. Derived from wxPython "wx.App".
    """

    def __init__(self, parameters, *args, **kargs):
        self.params = parameters
        self.alive = True
        self.redraw_pending = False
        self.connection_data = ConnectionData(self.params.control_host, self.params.control_port, self.params.pseudo)

        # Caution : wx.App.__init__ automatically calls OnInit(),
        # thus all data must be initialized before
        wx.App.__init__(self, *args, **kargs)
        UIProxyReceiver.__init__(self)

    def InitTwisted(self):
        """
        Import and initialize the Twisted event loop.
        Note: Twisted will run in a separate thread from the GUI.
        """

        from twisted.internet import reactor
        from twisted.python import threadable
        threadable.init(1)
        self.reactor = reactor

    def InitWx(self):
        """
        Initialize some wxWidgets stuff, including localization.
        """

        import locale as system_locale
        wx.InitAllImageHandlers()
        self.locale = wx.Locale()
        self.locale.Init2()
        try:
            translation_dir = self.params.translation_dir
            self.locale.AddCatalogLookupPathPrefix(translation_dir)
        except AttributeError:
            print "No translation dir specified"
            pass
        print self.locale.AddCatalog("solipsis")
        # Workaround for buggy Python behaviour with floats
        system_locale.setlocale(system_locale.LC_NUMERIC, "C")

    def OnInit(self):
        """
        Main initialization handler.
        """

        self.InitTwisted()
        self.InitWx()

        # Loading UI layout from XML file
        self.dialogs = ["about_dialog", "connect_dialog", "not_implemented_dialog"]
        self.windows = ["main_window"]
        self.menubars = ["main_menubar"]
        objects = self.dialogs + self.windows + self.menubars

        print sys.path
        self.LoadResource("resources/navigator.xrc")
        for obj_name in objects:
            self.__setattr__(obj_name, self.Resource(obj_name))

        # 2D viewport for the world view
        self.viewport_panel = XRCCTRL(self.main_window, "viewport_panel")
        self.viewport = Viewport(self.viewport_panel)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.viewport.JumpTo((0.5,0.5))
        self.world = World(self.viewport)

        # Putting objects together
        self.main_window.SetMenuBar(self.main_menubar)

        #self.test_panel = XRCCTRL(self.not_implemented_dialog, "test_panel")
        #b = wx.Button(self.test_panel, label=_("Close"))

        # Nicer sizing
        for obj_name in objects:
            attr = self.__getattribute__(obj_name)
            attr.SetSizeHintsSz(attr.GetBestVirtualSize())

        # Validators for various form controls
        c = self.connection_data
        validators = [
            # Containing window, control name, validator class, data object, data attribute
            [ self.connect_dialog, "connect_port", PortValidator, c, "port" ],
            [ self.connect_dialog, "connect_host", HostnameValidator, c, "host" ],
            [ self.connect_dialog, "connect_pseudo", NicknameValidator, c, "pseudo" ],
        ]
        for v in validators:
            window, control_name, validator_class, data_obj, data_attr = v
            validator = validator_class(data_obj.Ref(data_attr))
            XRCCTRL(window, control_name).SetValidator(validator)

        # UI events in main window
        wx.EVT_MENU(self, XRCID("menu_about"), self._About)
        wx.EVT_MENU(self, XRCID("menu_connect"), self._OpenConnect)
        wx.EVT_MENU(self, XRCID("menu_disconnect"), self._Disconnect)
        wx.EVT_MENU(self, XRCID("menu_preferences"), self._Preferences)
        wx.EVT_MENU(self, XRCID("menu_quit"), self._Quit)
        wx.EVT_CLOSE(self.main_window, self._Quit)

        # UI events in about dialog
        wx.EVT_CLOSE(self.about_dialog, self._CloseAbout)
        wx.EVT_BUTTON(self, XRCID("about_ok"), self._CloseAbout)

        # UI events in close dialog
        wx.EVT_CLOSE(self.connect_dialog, self._CloseConnect)
        wx.EVT_BUTTON(self, XRCID("connect_cancel"), self._CloseConnect)
        wx.EVT_BUTTON(self, XRCID("connect_ok"), self._ConnectOk)

        # UI events in not implemented dialog
        wx.EVT_CLOSE(self.not_implemented_dialog, self._CloseNotImplemented)
        wx.EVT_BUTTON(self, XRCID("not_implemented_ok"), self._CloseNotImplemented)

        # UI events in world viewport
        wx.EVT_LEFT_DOWN(self.viewport_panel, self._LeftClickViewport)

        # Let's go...
        # 1. Show UI on screen
        self.main_window.Show()
        self.SetTopWindow(self.main_window)

        # 2. Launch network event loop
        loop = NetworkLoop(self.reactor, self)
        loop.setDaemon(True)
        loop.start()
        self.network_loop = loop
        self.network = TwistedProxy(loop, self.reactor)

        # 3. Launch main GUI loop
        if os.name == 'posix' and wx.Platform == '__WXGTK__':
            self.x11 = True
        else:
            self.x11 = False
        return True


    def _NotImplemented(self, evt=None):
        """
        Displays a dialog warning that a function is not implemented.
        """

        #self.not_implemented_dialog.ShowModal()
        msg = _("This function is not yet implemented.\nSorry! Please come back later...")
        dialog = wx.MessageDialog(None, _(msg), caption=_("Not implemented"), style=wx.OK | wx.ICON_EXCLAMATION)
        dialog.ShowModal()

    def Redraw(self):
        """
        Redraw the world view.
        """
        self.viewport.Draw(onPaint=False)
        self.redraw_pending = False

    def AskRedraw(self):
        """
        This method tries hard to schedule redraws of the world view in a smart way.
        """
        if self.viewport.NeedsFurtherRedraw():
            if not self.viewport.PendingRedraw() and not self.redraw_pending:
                # This is a hack so that we don't take 100% CPU time
                # and give some timeslices to the X server
                self.redraw_pending = True
                t = self.viewport.LastRedrawDuration()
                wx.FutureCall(5.0 + 5 * 1000 * t, self.Redraw)
                return True
        return False

    def OnIdle(self, event):
        """
        Idle event handler. Used to smoothly redraw some things.
        """

        if self.alive:
            if not self.AskRedraw():
                event.Skip()
            else:
                self.ProcessPendingEvents()
        else:
            event.Skip()

    def OnPaint(self, event):
        """
        Called on repaint request.
        """

        self.viewport.Draw(onPaint=True)
        event.Skip()

    #===-----------------------------------------------------------------===#
    # Event handlers for the main window
    # (in alphabetical order)
    #
    def _About(self, evt):
        """ Called on "about" event (menu -> Help -> About). """
        self.about_dialog.ShowModal()

    def _OpenConnect(self, evt):
        """ Called on "connect" event (menu -> File -> Connect). """
        self.connect_dialog.ShowModal()

    def _Disconnect(self, evt):
        """ Called on "disconnect" event (menu -> File -> Disconnect). """
        self.network.DisconnectFromNode()

    def _Preferences(self, evt):
        """ Called on "preferences" event (menu -> File -> Preferences). """
        self._NotImplemented()

    def _Quit(self, evt):
        """ Called on quit event (menu -> File -> Quit, window close box). """

        self.alive = False
        # Disable event proxying: as of now, all UI -> network
        # and network -> UI events will be discarded
        self.DisableProxy()
        self.network.DisableProxy()
        # Process the last pending events
        self.ProcessPendingEvents()
        # Now we are sure that no more events are pending, kill everything
        self.reactor.crash()
        #self.network_loop.join()
        for obj_name in self.dialogs + self.windows:
            try:
                win = getattr(self, obj_name)
                win.DestroyChildren()
                win.Destroy()
            except:
                pass


    #===-----------------------------------------------------------------===#
    # Event handlers for the about dialog
    #
    def _CloseAbout(self, evt):
        """ Called on close "about dialog" event (Ok button, window close box). """
        self.about_dialog.Hide()


    #===-----------------------------------------------------------------===#
    # Event handlers for the "not implemented" dialog
    #
    def _CloseNotImplemented(self, evt):
        """ Called on close "not implemented dialog" event (Ok button, window close box). """
        self.not_implemented_dialog.Hide()


    #===-----------------------------------------------------------------===#
    # Event handlers for the connect dialog
    #
    def _CloseConnect(self, evt):
        """ Called on close "connect dialog" event (Cancel button, window close box). """
        self.connect_dialog.Hide()

    def _ConnectOk(self, evt):
        """ Called on connect submit event (Ok button). """
        if (self.connect_dialog.Validate()):
            self.connect_dialog.Hide()
            self.network.ConnectToNode(self.connection_data.host, self.connection_data.port)
            self.viewport.Reset()


    #===-----------------------------------------------------------------===#
    # Event handlers for the world viewport
    #
    def _LeftClickViewport(self, evt):
        """ Called on left click event. """
        x, y = self.viewport.MoveToPixels(evt.GetPositionTuple())
        self.network.MoveTo((x, y))
        evt.Skip()


    #===-----------------------------------------------------------------===#
    # Actions from the network thread(s)
    #
    def AddPeer(self, *args, **kargs):
        """ Add an object to the viewport. """
        self.world.AddPeer(*args, **kargs)

    def MovePeer(self, *args, **kargs):
        """ Move an object in the viewport. """
#         self.viewport.MoveObject(*args, **kargs)

    def RemovePeer(self, *args, **kargs):
        """ Remove an object from the viewport. """
        self.world.RemovePeer(*args, **kargs)

    def UpdateNode(self, *args, **kargs):
        """ Update node information. """
        self.world.UpdateNode(*args, **kargs)

    def ResetWorld(self, *args, **kargs):
        """ Reset the viewport. """
        self.world.Reset(*args, **kargs)

