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
import gc
import sys
import wx
import wx.xrc
import bisect
from wx.xrc import XRCCTRL, XRCID

from solipsis.util.entity import ServiceData
from solipsis.util.uiproxy import TwistedProxy, UIProxyReceiver
from solipsis.util.wxutils import _
from solipsis.util.wxutils import *        # '*' doesn't import '_'
from solipsis.util.memdebug import MemSizer

from validators import *
from viewport import Viewport
from world import World
from statusbar import StatusBar
from network import NetworkLoop
from config import ConfigUI, ConfigData

from solipsis.services.collector import ServiceCollector


class NavigatorApp(wx.App, XRCLoader, UIProxyReceiver):
    """
    Main application class. Derived from wxPython "wx.App".
    """

    def __init__(self, params, *args, **kargs):
        self.params = params
        self.alive = True
        self.redraw_pending = False
        self.config_data = ConfigData()
        self.node_proxy = None
        if self.params.memdebug:
            self.memsizer = MemSizer()
            #~ gc.set_debug(gc.DEBUG_LEAK)
        else:
            self.memsizer = None

        self.dialogs = None
        self.windows = None
        self.menubars = None
        
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
        Initialize some basic wxWidgets stuff, including localization.
        """
        import locale as system_locale
        wx.InitAllImageHandlers()
        self.locale = wx.Locale()
        self.locale.Init2()
        try:
            translation_dir = self.params.translation_dir
        except AttributeError:
            print "No translation dir specified"
            pass
        else:
            self.locale.AddCatalogLookupPathPrefix(translation_dir)
            self.locale.AddCatalog("solipsis")
        # Workaround for buggy Python behaviour with floats
        system_locale.setlocale(system_locale.LC_NUMERIC, "C")

    def InitResources(self):
        """
        Load UI layout from XML file(s).
        """
        self.dialogs = [
            "about_dialog",
            "connect_dialog",
            "prefs_dialog",
        ]
        self.windows = ["main_window"]
        self.menubars = ["main_menubar"]
        objects = self.dialogs + self.windows + self.menubars

        self.LoadResource("resources/navigator.xrc")
        for obj_name in objects:
            self.__setattr__(obj_name, self.Resource(obj_name))

        # 2D viewport for the world view
        self.viewport_panel = XRCCTRL(self.main_window, "viewport_panel")
        self.viewport = Viewport(self.viewport_panel)

        # Putting objects together
        self.main_window.SetMenuBar(self.main_menubar)
        self.statusbar = StatusBar(self.main_window, _("Not connected"))

        # Nicer sizing
        for obj_name in objects:
            attr = self.__getattribute__(obj_name)
            attr.SetSizeHintsSz(attr.GetBestVirtualSize())

    def InitValidators(self):
        """
        Setup validators for various form controls.
        Validators have two purposes :
        1. Validate proper data is entered in forms
        2. Transfer validated data to their storage location 
           (an instance variable of a ManagedData subclass instance).
        """
        c = self.config_data
        validators = [
            # [ Containing window, control name, validator class, data object, data attribute ]
            [ self.connect_dialog, "connect_host", HostnameValidator, c, "host" ],
            [ self.connect_dialog, "connect_port", PortValidator, c, "port" ],
            [ self.connect_dialog, "connect_pseudo", NicknameValidator, c, "pseudo" ],
            [ self.prefs_dialog, "proxymode_auto", BooleanValidator, c, "proxymode_auto" ],
            [ self.prefs_dialog, "proxymode_manual", BooleanValidator, c, "proxymode_manual" ],
            [ self.prefs_dialog, "proxy_host", HostnameValidator, c, "proxy_host" ],
            [ self.prefs_dialog, "proxy_port", PortValidator, c, "proxy_port" ],
        ]
        for v in validators:
            window, control_name, validator_class, data_obj, data_attr = v
            validator = validator_class(data_obj.Ref(data_attr))
            XRCCTRL(window, control_name).SetValidator(validator)

    def InitServices(self):
        """
        Initialize all services.
        """
        # We will insert service menus just before the last menu,
        # which is the "Help" menu
        self.service_menus = []
        self.service_menu_pos = self.main_menubar.GetMenuCount() - 1
        self.services.ReadServices()
        self.services.SetNode(self.config_data.GetNode())
        self.services.EnableServices()
        self.config_data.SetServices(self.services.GetServices())

    def OnInit(self):
        """
        Main initialization handler.
        """

        self.InitTwisted()
        self.InitWx()
        self.InitResources()
        self.InitValidators()

        self.world = World(self.viewport)
        self.config_ui = ConfigUI(self.config_data, self.prefs_dialog)

        # UI events in main window
        wx.EVT_MENU(self, XRCID("menu_about"), self._About)
        wx.EVT_MENU(self, XRCID("menu_connect"), self._OpenConnect)
        wx.EVT_MENU(self, XRCID("menu_disconnect"), self._Disconnect)
        wx.EVT_MENU(self, XRCID("menu_kill"), self._Kill)
        wx.EVT_MENU(self, XRCID("menu_preferences"), self._Preferences)
        wx.EVT_MENU(self, XRCID("menu_quit"), self._Quit)
        wx.EVT_MENU(self, XRCID("menu_autorotate"), self._ToggleAutoRotate)
        wx.EVT_CLOSE(self.main_window, self._Quit)

        # UI events in about dialog
        wx.EVT_CLOSE(self.about_dialog, self._CloseAbout)
        wx.EVT_BUTTON(self, XRCID("about_ok"), self._CloseAbout)

        # UI events in connect dialog
        wx.EVT_CLOSE(self.connect_dialog, self._CloseConnect)
        wx.EVT_BUTTON(self, XRCID("connect_cancel"), self._CloseConnect)
        wx.EVT_BUTTON(self, XRCID("connect_ok"), self._ConnectOk)

        # UI events in world viewport
        wx.EVT_IDLE(self.viewport_panel, self.OnIdle)
        wx.EVT_PAINT(self.viewport_panel, self.OnPaint)
        wx.EVT_SIZE(self.viewport_panel, self.OnResize)
        wx.EVT_LEFT_DOWN(self.viewport_panel, self._LeftClickViewport)
        wx.EVT_RIGHT_UP(self.viewport_panel, self._RightClickViewport)
        wx.EVT_MOTION(self.viewport_panel, self._HoverViewport)

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
        
        if self.memsizer:
            self._MemDebug()
        
        # 4. Other tasks are launched after the window is drawn
        self.services = ServiceCollector(self.params, self, self.reactor)
        #~ wx.FutureCall(500, self.InitServices)
        wx.CallAfter(self.InitServices)
        
        return True


    def Redraw(self):
        """
        Redraw the world view.
        """
        self.viewport.Draw(onPaint=False)

    def AskRedraw(self):
        """
        This method tries hard to schedule redraws of the world view in a smart way.
        """
        if self.viewport.NeedsFurtherRedraw():
            if not self.viewport.PendingRedraw() and not self.redraw_pending:
                # This is a hack so that we don't take too much CPU time
                # and give some timeslices to the graphics subsystem
                self.redraw_pending = True
                if self.x11:
                    t = 5.0 + 5 * 1000 * self.viewport.LastRedrawDuration()
                else:
                    t = 5.0
                def _redraw():
                    self.redraw_pending = False
                    self.Redraw()
                wx.FutureCall(t, _redraw)
                #~ wx.FutureCall(t, self.Redraw)
                #~ wx.CallAfter(self.Redraw)
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

    def OnResize(self, event):
        """
        Called on repaint request.
        """
        self.Redraw()

    #
    # Helpers
    #
    def _NotImplemented(self, evt=None):
        """
        Displays a dialog warning that a function is not implemented.
        """
        #self.not_implemented_dialog.ShowModal()
        msg = _("This function is not yet implemented.\nSorry! Please come back later...")
        dialog = wx.MessageDialog(None, msg, caption=_("Not implemented"), style=wx.OK | wx.ICON_EXCLAMATION)
        dialog.ShowModal()

    def _CheckNodeProxy(self, display_error=True):
        """
        Checks if we are connected to a node, if not, displays a message box.
        Returns True if we are connected, False otherwise.
        """
        if self.node_proxy is not None:
            return True
        if display_error:
            msg = _("This action cannot be performed, \nbecause you are not connected to a node.")
            dialog = wx.MessageDialog(None, msg, caption=_("Not connected"), style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
        return False
    
    def _MemDebug(self):
        import gc
        gc.collect()
        self.memsizer.sizeall()
        print "\n... memdump ...\n"
        items = self.memsizer.get_deltas()
        print "\n".join(items)
        wx.FutureCall(1000.0 * 10, self._MemDebug)
        #~ print "\ngarbage:", gc.garbage
        print "\n\n"

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
        if self._CheckNodeProxy():
            self.network.DisconnectFromNode()
            self.node_proxy = None
            self.viewport.Disable()
            self.Redraw()
            self.statusbar.SetText(_("Not connected"))
            self.services.RemoveAllPeers()

    def _Kill(self, evt):
        """ Called on "kill" event (menu -> File -> Kill). """
        if self._CheckNodeProxy():
            self.network.KillNode()
            self.services.RemoveAllPeers()

    def _Preferences(self, evt):
        """ Called on "preferences" event (menu -> File -> Preferences). """
        self.config_data.Autocomplete()
        self.prefs_dialog.Show()

    def _Quit(self, evt):
        """ Called on quit event (menu -> File -> Quit, window close box). """

        print evt
        self.alive = False
        # Disable event proxying: as of now, all UI -> network
        # and network -> UI events will be discarded
        self.DisableProxy()
        self.network.DisableProxy()
        # Process the last pending events
        self.ProcessPendingEvents()
        # Finish running services
        self.services.Finish()
        # Now we are sure that no more events are pending, kill everything
        self.reactor.crash()
        for obj_name in self.dialogs + self.windows:
            try:
                win = getattr(self, obj_name)
                win.Destroy()
            except:
                pass

    def _ToggleAutoRotate(self, evt):
        """ Called on autorotate event (menu -> View -> Autorotate). """
        
        self.viewport.AutoRotate(evt.IsChecked())


    #===-----------------------------------------------------------------===#
    # Event handlers for the about dialog
    #
    def _CloseAbout(self, evt):
        """ Called on close "about dialog" event (Ok button, window close box). """
        self.about_dialog.Hide()


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
            self.config_data.Autocomplete()
            self.network.ConnectToNode(self.config_data)
            self.viewport.Reset()
            self.statusbar.SetText(_("Connecting"))
            self.services.RemoveAllPeers()
            self.services.SetNode(self.config_data.GetNode())


    #===-----------------------------------------------------------------===#
    # Event handlers for the world viewport
    #
    def _LeftClickViewport(self, evt):
        """ Called on left click event. """
        if self._CheckNodeProxy(False):
            x, y = self.viewport.MoveToPixels(evt.GetPositionTuple())
            self.node_proxy.Move(str(long(x)), str(long(y)), str(0))
        evt.Skip()

    def _RightClickViewport(self, evt):
        """ Called on left click event. """
        # We display a contextual menu
        menu = wx.Menu()
        if self._CheckNodeProxy(False):
            id_ = self.viewport.HoveredItem()
            if id_ is not None:
                menu.Append(wx.NewId(), _('Peer "%s"') % self.world.GetPeer(id_).pseudo)
                menu.AppendSeparator()
            l = self.services.GetPopupMenuItems(menu)
            if len(l) > 0:
                for item in l:
                    menu.AppendItem(item)
                menu.AppendSeparator()
            menu.Append(XRCID("menu_disconnect"), _("Disconnect"))
        else:
            menu.Append(XRCID("menu_connect"), _("Connect to node"))
        menu.Append(XRCID("menu_about"), _("About Solipsis"))
        self.viewport_panel.PopupMenu(menu)
        evt.Skip()

    def _HoverViewport(self, evt):
        """ Called on mouse movement. """
        if self._CheckNodeProxy(False):
            x, y = evt.GetPositionTuple()
            changed, id_ = self.viewport.Hover((x, y))
            if changed and id_:
                self.statusbar.SetTemp(self.world.GetPeer(id_).pseudo)
            elif changed and not id_:
                self.statusbar.Reset()
        evt.Skip()


    #===-----------------------------------------------------------------===#
    # Actions from the network thread(s)
    #
    def AddPeer(self, *args, **kargs):
        """ Add an object to the viewport. """
        self.world.AddPeer(*args, **kargs)
        self.services.AddPeer(*args, **kargs)

    def RemovePeer(self, *args, **kargs):
        """ Remove an object from the viewport. """
        self.world.RemovePeer(*args, **kargs)
        self.services.RemovePeer(*args, **kargs)

    def UpdatePeer(self, *args, **kargs):
        """ Update an object. """
        self.world.UpdatePeer(*args, **kargs)
        self.services.UpdatePeer(*args, **kargs)

    def UpdateNode(self, *args, **kargs):
        """ Update node information. """
        self.world.UpdateNode(*args, **kargs)
    
    def ProcessServiceData(self, *args, **kargs):
        """ Process service-specific data. """
        self.services.ProcessServiceData(*args, **kargs)

    def ResetWorld(self, *args, **kargs):
        """ Reset the viewport. """
        self.world.Reset(*args, **kargs)

    def SetStatus(self, status):
        """ Change connection status. """
        if status == 'READY':
            self.viewport_panel.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            self.viewport.Enable()
            self.Redraw()
            self.statusbar.SetText(_("Connected"))
        elif status == 'BUSY':
            self.viewport_panel.SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
            self.viewport.Enable()
            self.Redraw()
            self.statusbar.SetText(_("Searching peers"))
        elif status == 'UNAVAILABLE':
            self.viewport_panel.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            self.viewport.Disable()
            self.Redraw()
            self.statusbar.SetText(_("Not connected"))

    def NodeConnectionSucceeded(self, node_proxy):
        """ We managed to connect to the node. """
        # We must call the node proxy from the Twisted thread!
        self.node_proxy = TwistedProxy(node_proxy, self.reactor)
        self.node_proxy.SetNodeInfo(self.config_data.GetNode().ToStruct())
        self.statusbar.SetText(_("Connected"))

    def NodeConnectionFailed(self, error):
        """ Failed connecting to the node. """
        self.node_proxy = None
        self.statusbar.SetText(_("Not connected"))
        msg = _("Connection to the node has failed. \nPlease the check the node is running, then retry.")
        dialog = wx.MessageDialog(None, msg, caption=_("Connection error"), style=wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()

    def NodeKillSucceeded(self):
        """ We managed to kill the (remote/local) node. """
        self.node_proxy = None
        self.viewport.Disable()
        self.Redraw()
        self.statusbar.SetText(_("Not connected"))

    def NodeKillFailed(self):
        """ The node refused to kill itself. """
        self.node_proxy = None
        self.viewport.Disable()
        msg = _("You cannot kill this node.")
        dialog = wx.MessageDialog(None, msg, caption=_("Kill refused"), style=wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()

    #===-----------------------------------------------------------------===#
    # Actions from the services
    #
    def SetServiceMenu(self, service_id, title, menu):
        val = (title, service_id)
        pos = bisect.bisect_right(self.service_menus, val)
        if pos == len(self.service_menus) or self.service_menus[pos][1] != service_id:
            self.main_menubar.Insert(pos + self.service_menu_pos, menu, title)
            self.service_menus.insert(pos, val)
        else:
            self.main_menubar.Replace(pos + self.service_menu_pos, menu, title)
            self.service_menus[pos] = val

    def SendServiceData(self, peer_id, service_id, data):
        if self._CheckNodeProxy(False):
            d = ServiceData(peer_id, service_id, data)
            self.node_proxy.SendServiceData(d.ToStruct())
