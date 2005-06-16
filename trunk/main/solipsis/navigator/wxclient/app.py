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
import sys
import gc
import wx
import wx.xrc
import bisect
import re
from wx.xrc import XRCCTRL, XRCID

from solipsis.util.entity import ServiceData
from solipsis.util.address import Address
from solipsis.util.urls import SolipsisURL
from solipsis.util.position import Position
from solipsis.util.uiproxy import TwistedProxy, UIProxyReceiver
from solipsis.util.wxutils import _
from solipsis.util.wxutils import *        # '*' doesn't import '_'
from solipsis.util.urlhandlers import SetSolipsisURLHandlers
from solipsis.util.memdebug import MemSizer
from solipsis.util.launch import Launcher

from validators import *
from viewport import Viewport
from world import World
from statusbar import StatusBar
from network import NetworkLoop
from config import ConfigData

from BookmarksDialog import BookmarksDialog
from ConnectDialog import ConnectDialog
from PreferencesDialog import PreferencesDialog
from PositionJumpDialog import PositionJumpDialog

from solipsis.services.wxcollector import WxServiceCollector


class NavigatorApp(wx.App, XRCLoader, UIProxyReceiver):
    """
    Main application class. Derived from wxPython "wx.App".
    """
    version = "0.8.4svn"
    config_file = os.sep.join(["state", "config.bin"])
    world_size = 2**128

    def __init__(self, params, *args, **kargs):
        self.params = params
        self.alive = True
        self.redraw_pending = False
        self.config_data = ConfigData(self.params)
        self.node_proxy = None
        if self.params.memdebug:
            self.memsizer = MemSizer()
            #~ gc.set_debug(gc.DEBUG_LEAK)
        else:
            self.memsizer = None

        self.dialogs = None
        self.windows = None
        self.menubars = None

        self.progress_dialog = None
        self.url_jump = self.params.url_jump or None

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
        if not self.locale.Init2() and wx.Platform != '__WXMSW__':
            print "Error: failed to initialize wx.Locale!"
            print "If you are under Linux or Un*x, check the LC_MESSAGES or LANG environment variable is properly set."
            sys.exit(1)
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
            # Avoid crash on MacOS X
            if isinstance(attr, wx.MenuBar):
                continue
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
            #~ [ self.prefs_dialog, "proxymode_auto", BooleanValidator, c, "proxymode_auto" ],
        ]
        for v in validators:
            window, control_name, validator_class, data_obj, data_attr = v
            validator = validator_class(data_obj.Ref(data_attr))
            XRCCTRL(window, control_name).SetValidator(validator)

    def InitNetwork(self):
        """
        Launch network event loop.
        """
        loop = NetworkLoop(self.reactor, self)
        loop.setDaemon(True)
        loop.start()
        self.network_loop = loop
        self.network = TwistedProxy(loop, self.reactor)
        self.network.StartURLListener(self.params.url_port_min, self.params.url_port_max)
        SetSolipsisURLHandlers()

    def InitServices(self):
        """
        Initialize all services.
        """
        self.services = WxServiceCollector(self.params, self, self.reactor)
        # Service-specific menus in the menubar: We will insert service menus
        # just before the last menu, which is the "Help" menu
        self.service_menus = []
        self.service_menu_pos = self.main_menubar.GetMenuCount() - 1

        self.services.ReadServices()
        self.services.SetNode(self.config_data.GetNode())
        self.services.EnableServices()
        self.config_data.SetServices(self.services.GetServices())

        # If the menu has become too wide because of the entries added by services,
        # resize main window so that the menu fits
        # BUG: this doesn't work :(
        self.main_menubar.Layout()
        self.main_window.Layout()
        self.main_window.SetSize(self.main_window.GetBestVirtualSize())

    def OnInit(self):
        """
        Main initialization handler.
        """
        # Load last saved config
        try:
            f = file(self.config_file, "rb")
            self.config_data.Load(f)
        except (IOError, EOFError):
            if os.path.exists(self.config_file):
                print "Config file '%s' broken, erasing"
                os.remove(self.config_file)

        self.InitWx()
        self.InitResources()
        self.InitValidators()

        self.world = World(self.viewport)
        bookmarks_menu = self.main_menubar.GetMenu(self.main_menubar.FindMenu(_("&Bookmarks")))
        assert bookmarks_menu is not None
        # Hack: we store the bookmarks dialog persistently because it
        # also interacts with the menubar (ssshh..)
        self.bookmarks_dialog = BookmarksDialog(app=self,
            world=self.world,
            config_data=self.config_data,
            menu=bookmarks_menu,
            parent=self.main_window)
        self.bookmarks_dialog.UpdateUI()

        # UI events in main window
        wx.EVT_MENU(self, XRCID("menu_about"), self._OnAbout)
        wx.EVT_MENU(self, XRCID("menu_connect"), self._OnConnect)
        wx.EVT_MENU(self, XRCID("menu_disconnect"), self._OnDisconnect)
        wx.EVT_MENU(self, XRCID("menu_kill"), self._OnKill)
        wx.EVT_MENU(self, XRCID("menu_jumpnear"), self._OnJumpNear)
        wx.EVT_MENU(self, XRCID("menu_jumppos"), self._OnJumpPos)
        wx.EVT_MENU(self, XRCID("menu_preferences"), self._OnPreferences)
        wx.EVT_MENU(self, XRCID("menu_quit"), self._OnQuit)
        wx.EVT_MENU(self, XRCID("menu_autorotate"), self._OnToggleAutoRotate)
        wx.EVT_MENU(self, XRCID("menu_nodeaddr"), self._OnDisplayAddress)
        wx.EVT_MENU(self, XRCID("menu_edit_bookmarks"), self._OnEditBookmarks)
        wx.EVT_CLOSE(self.main_window, self._OnQuit)

        # UI events in world viewport
        wx.EVT_IDLE(self.viewport_panel, self.OnIdle)
        wx.EVT_PAINT(self.viewport_panel, self.OnPaint)
        wx.EVT_SIZE(self.viewport_panel, self.OnResize)
        wx.EVT_LEFT_DOWN(self.viewport_panel, self._OnLeftClickViewport)
        wx.EVT_RIGHT_DOWN(self.viewport_panel, self._OnRightClickViewport)
        wx.EVT_MOTION(self.viewport_panel, self._OnHoverViewport)
        # For portability we need both
        wx.EVT_CHAR(self.main_window, self._OnKeyPressViewport)
        wx.EVT_CHAR(self.viewport_panel, self._OnKeyPressViewport)

        # Let's go...
        # 1. Show UI on screen
        self.main_window.Show()
        self.SetTopWindow(self.main_window)

        # 2. Launch main GUI loop
        if os.name == 'posix' and wx.Platform == '__WXGTK__':
            self.x11 = True
        else:
            self.x11 = False
        
        if self.memsizer:
            self._MemDebug()
        
        # 3. Other tasks are launched after the window is drawn
        wx.CallAfter(self.InitTwisted)
        wx.CallAfter(self.InitNetwork)
        wx.CallAfter(self.InitServices)
        
        # 4. Automatic connection window at start
        wx.CallAfter(self._OpenConnectDialog)
        
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
        gc.collect()
        self.memsizer.sizeall()
        print "\n... memdump ...\n"
        items = self.memsizer.get_deltas()
        print "\n".join(items)
        wx.FutureCall(1000.0 * 10, self._MemDebug)
        #~ print "\ngarbage:", gc.garbage
        print "\n\n"
    
    def _JumpNearAddress(self, address):
        if self._CheckNodeProxy():
            self.node_proxy.JumpNear(address.ToStruct())
    
    def _JumpNearURL(self, url_string):
        print "Received:", url_string
        if self._CheckNodeProxy(False):
            try:
                url = SolipsisURL.FromString(url_string)
            except ValueError, e:
                print str(e)
            else:
                self._JumpNearAddress(url.GetAddress())
            self.url_jump = None
        else:
            self.url_jump = url_string
    
    def _UpdateURLPort(self, url_port):
        filename = os.path.join('state', 'url_jump.port')
        f = file(filename, 'wb')
        f.write(str(url_port))
        f.close()
    
    def _OpenConnectDialog(self):
        connect_dialog = ConnectDialog(config_data=self.config_data, parent=self.main_window)
        if connect_dialog.ShowModal() != wx.ID_OK:
            return
        self.config_data.Compute()
        if self.config_data.connection_type == 'local':
            # Local connection mode: create a dedicated Solipsis node
            self._LaunchNode()
        else:
            # Remote connection mode: connect to an existing node
            self.connection_trials = 0
            self._TryConnect()
    
    def _TryConnect(self):
        """
        Tries to connect to the configured node.
        """
        if self._CheckNodeProxy(False):
            self.network.DisconnectFromNode()
        self._SetWaiting(True)
        self.world.Reset()
        self.viewport.Reset()
        self.network.ConnectToNode(self.config_data)
        self.statusbar.SetText(_("Connecting"))
        self.services.RemoveAllPeers()
        self.services.SetNode(self.config_data.GetNode())

    def _LaunchNode(self):
        self.config_data.Compute()
        l = Launcher(port=self.config_data.solipsis_port,
            control_port=self.config_data.local_control_port)
        # First try to spawn the node
        if not l.Launch():
            self.viewport.Disable()
            msg = _("Node creation failed. \nPlease check you have sufficient rights.")
            dialog = wx.MessageDialog(None, msg, caption=_("Kill refused"), style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return
        # Then connect using its XMLRPC daemon
        # Hack so that the node has the time to launch
        self.connection_trials = 5
        self._TryConnect()

    def _MoveNode(self, (x, y), jump=False):
        """
        Move the node and update our world view.
        """
        self.world.UpdateNodePosition(Position((x, y, 0)), jump=jump)
        self.node_proxy.Move(str(long(x)), str(long(y)), str(0))

    def _DestroyProgress(self):
        """
        Destroy progress dialog if necessary.
        """
        if self.progress_dialog is not None:
            self.progress_dialog.Destroy()
            self.progress_dialog = None
    
    def _SetWaiting(self, waiting):
        """
        Set "waiting" state of the interface.
        """
        if waiting:
            cursor = wx.StockCursor(wx.CURSOR_ARROWWAIT)
        else:
            cursor = wx.StockCursor(wx.CURSOR_DEFAULT)
        self.viewport_panel.SetCursor(cursor)
    
    def _HandleMouseMovement(self, evt):
        """
        Handle the mouse position part of a mouse event.
        """
        x, y = evt.GetPositionTuple()
        changed, id_ = self.viewport.Hover((x, y))
        if changed and id_:
            self.statusbar.SetTemp(self.world.GetPeer(id_).pseudo)
        elif changed and not id_:
            self.statusbar.Reset()

    def _SaveConfig(self):
        """
        Save current configuration to the user's config file.
        """
        try:
            f = file(self.config_file, "wb")
            self.config_data.Save(f)
            f.close()
        except IOError, e:
            print "Failed to saved config:", str(e)


    #===-----------------------------------------------------------------===#
    # Event handlers for the main window
    # (in alphabetical order)
    #
    def _OnAbout(self, evt):
        """
        Called on "about" event (menu -> Help -> About).
        """
        msg = _("Solipsis Navigator") + " " + self.version + "\n\n" + _("Licensed under the GNU LGPL") + "\n(c) France Telecom R&D"
        dialog = wx.MessageDialog(None, msg, caption=_("About..."), style=wx.OK | wx.ICON_INFORMATION)
        dialog.ShowModal()

    def _OnEditBookmarks(self, evt):
        """
        Called on "edit bookmarks" event (menu -> Bookmarks -> Edit bookmarks).
        """
        self.bookmarks_dialog.Show()

    def _OnConnect(self, evt):
        """
        Called on "connect" event (menu -> File -> Connect).
        """
        self._OpenConnectDialog()

    def _OnDisconnect(self, evt):
        """
        Called on "disconnect" event (menu -> File -> Disconnect).
        """
        self._DestroyProgress()
        self._SetWaiting(False)
        if self._CheckNodeProxy():
            self.network.DisconnectFromNode()
            self.node_proxy = None
            self.viewport.Disable()
            self.Redraw()
            self.statusbar.SetText(_("Not connected"))
            self.services.RemoveAllPeers()

    def _OnDisplayAddress(self, evt):
        """
        Called on "node address" event (menu -> Actions -> Jump Near).
        """
        if self._CheckNodeProxy():
            address_str = self.world.GetNode().address.ToString()
            clipboard = wx.TheClipboard
            clipboard.Open()
            clipboard.SetData(wx.TextDataObject(address_str))
            clipboard.Close()
            msg = _("Your address has been copied to the clipboard. \nIf you paste it and send it to your friends, \nthey will be able to jump near you in the Solipsis world.")
            msg += "\n\n" + _("For reminder, here is your address:") + "\n" + address_str
            dialog = wx.MessageDialog(self.main_window,
                message=msg,
                caption=_("Your Solipsis address"),
                style=wx.OK|wx.CENTRE|wx.ICON_INFORMATION
                )
            dialog.ShowModal()

    def _OnJumpNear(self, evt):
        """
        Called on "jump near" event (menu -> Actions -> Jump near).
        """
        if self._CheckNodeProxy():
            dialog = wx.TextEntryDialog(self.main_window,
                message=_("Please enter the address to jump to"),
                caption=_("Jump near an entity"),
                defaultValue='slp://192.33.178.29:5010/'
                )
            if dialog.ShowModal() == wx.ID_OK:
                v = dialog.GetValue()
                try:
                    address = Address.FromString(v)
                except ValueError, e:
                    self._JumpNearURL(v)
                else:
                    self._JumpNearAddress(address)

    def _OnJumpPos(self, evt):
        """
        Called on "jump to position" event (menu -> Actions -> Jump to position).
        """
        if not self._CheckNodeProxy():
            return
        jump_dialog = PositionJumpDialog(config_data=self.config_data, parent=self.main_window)
        if jump_dialog.ShowModal() == wx.ID_OK:
            x, y = jump_dialog.GetPosition()
            self._MoveNode((x * self.world_size, y * self.world_size), jump=True)

    def _OnKill(self, evt):
        """
        Called on "kill" event (menu -> File -> Kill).
        """
        if self._CheckNodeProxy():
            self.network.KillNode()
            self.services.RemoveAllPeers()

    def _OnPreferences(self, evt):
        """
        Called on "preferences" event (menu -> File -> Preferences).
        """
        self.config_data.Compute()
        prefs_dialog = PreferencesDialog(config_data=self.config_data, parent=self.main_window)
        prefs_dialog.ShowModal()
        self._SaveConfig()

    def _OnQuit(self, evt):
        """
        Called on quit event (menu -> File -> Quit, window close box).
        """
        self.alive = False
        self._SaveConfig()
        # Kill progress window
        self._DestroyProgress()
        # Kill the node if necessary
        if self.config_data.node_autokill and self._CheckNodeProxy(False):
            self.network.KillNode()
            self._SetWaiting(True)
            # Timeout in case the Kill request takes too much time to finish
            wx.FutureCall(1000, self._Quit2)
        else:
            self._Quit2()
    
    def _Quit2(self):
        """
        The end of the quit procedure ;-)
        """
        # Disable event proxying: as of now, all UI -> network
        # and network -> UI events will be discarded
        self.DisableProxy()
        self.network.DisableProxy()
        # Process the last pending events
        self.ProcessPendingEvents()
        # Finish running services
        self.services.Finish()
        # Now we are sure that no more events are pending, kill everything
        self.reactor.stop()
        for obj_name in self.dialogs + self.windows:
            try:
                win = getattr(self, obj_name)
                win.Destroy()
            except:
                pass

    def _OnToggleAutoRotate(self, evt):
        """
        Called on autorotate event (menu -> View -> Autorotate).
        """
        self.viewport.AutoRotate(evt.IsChecked())


    #===-----------------------------------------------------------------===#
    # Event handlers for the about dialog
    #
    def _CloseAbout(self, evt):
        """
        Called on close "about dialog" event (Ok button, window close box).
        """
        self.about_dialog.Hide()


    #===-----------------------------------------------------------------===#
    # Event handlers for the world viewport
    #
    def _OnKeyPressViewport(self, evt):
        """
        Called when a key is pressed.
        """
        if self._CheckNodeProxy(False):
            dx = 0.0
            dy = 0.0
            key = evt.GetKeyCode()
            if key == wx.WXK_UP:
                dy -= 0.3
            elif key == wx.WXK_DOWN:
                dy += 0.3
            elif key == wx.WXK_LEFT:
                dx -= 0.3
            elif key == wx.WXK_RIGHT:
                dx += 0.3
            else:
                evt.Skip()
            if dx or dy:
                x, y = self.viewport.MoveToRelative((dx, dy))
                self._MoveNode((x, y))
        else:
            evt.Skip()

    def _OnLeftClickViewport(self, evt):
        """
        Called on left click event.
        """
        if self._CheckNodeProxy(False):
            # First update our position (due to buggy EVT_MOTION handling)
            self._HandleMouseMovement(evt)
            # Then handle mouse click
            x, y = self.viewport.MoveToPixels(evt.GetPositionTuple())
            self._MoveNode((x, y))
        evt.Skip()

    def _OnRightClickViewport(self, evt):
        """
        Called on right click event.
        """
        # We display a contextual menu
        menu = wx.Menu()
        if self._CheckNodeProxy(False):
            # First update our position (due to buggy EVT_MOTION handling)
            self._HandleMouseMovement(evt)
            # Then get ID of the hovered peer, if any
            id_ = self.viewport.HoveredItem()
            # MenuItem #1: bookmark peer
            if id_ is not None:
                item_id = wx.NewId()
                peer = self.world.GetPeer(id_)
                menu.Append(item_id, _('Bookmark peer "%s"') % peer.pseudo)
                menu.AppendSeparator()
                # TODO: model-view-controller ?
                def _clicked(evt):
                    self.config_data.bookmarks.AddPeer(peer)
                    self.bookmarks_dialog.UpdateUI()
                wx.EVT_MENU(self.main_window, item_id, _clicked)

            # Following MenuItems are filled by service plugins
            l = self.services.GetPopupMenuItems(menu, id_)
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

    def _OnHoverViewport(self, evt):
        """
        Called on mouse movement in the viewport.
        """
        if self._CheckNodeProxy(False):
            self._HandleMouseMovement(evt)
        evt.Skip()


    #===-----------------------------------------------------------------===#
    # Actions from the network thread(s)
    #
    def AddPeer(self, *args, **kargs):
        """
        Add an object to the viewport.
        """
        self.world.AddPeer(*args, **kargs)
        self.services.AddPeer(*args, **kargs)

    def RemovePeer(self, *args, **kargs):
        """
        Remove an object from the viewport.
        """
        self.world.RemovePeer(*args, **kargs)
        self.services.RemovePeer(*args, **kargs)

    def UpdatePeer(self, *args, **kargs):
        """
        Update an object.
        """
        self.world.UpdatePeer(*args, **kargs)
        self.services.UpdatePeer(*args, **kargs)

    def UpdateNode(self, *args, **kargs):
        """
        Update node information.
        """
        self.services.SetNode(*args, **kargs)
        self.world.UpdateNode(*args, **kargs)
    
    def UpdateNodePosition(self, *args, **kargs):
        """
        Update node position.
        """
        self.world.UpdateNodePosition(*args, **kargs)
    
    def ProcessServiceData(self, *args, **kargs):
        """
        Process service-specific data.
        """
        self.services.ProcessServiceData(*args, **kargs)

    def ResetWorld(self, *args, **kargs):
        """
        Reset the world and the viewport.
        """
        self.world.Reset(*args, **kargs)

    def SetStatus(self, status):
        """
        Change connection status.
        """
        if status == 'READY':
            self._SetWaiting(False)
            self.viewport.Enable()
            self.Redraw()
            self.statusbar.SetText(_("Connected"))
        elif status == 'BUSY':
            self._SetWaiting(True)
            self.viewport.Enable()
            self.Redraw()
            self.statusbar.SetText(_("Searching peers"))
        elif status == 'UNAVAILABLE':
            self._SetWaiting(False)
            self.viewport.Disable()
            self.Redraw()
            self.statusbar.SetText(_("Not connected"))
        if self.url_jump:
            self._JumpNearURL(self.url_jump)

    def NodeConnectionSucceeded(self, node_proxy):
        """
        We managed to connect to the node.
        """
        self._DestroyProgress()
        self._SetWaiting(False)
        # We must call the node proxy from the Twisted thread!
        self.node_proxy = TwistedProxy(node_proxy, self.reactor)
        self.node_proxy.SetNodeInfo(self.config_data.GetNode().ToStruct())
        self.statusbar.SetText(_("Connected"))

    def NodeConnectionFailed(self, error):
        """
        Failed connecting to the node.
        """
        # Allow for some leeway in certain cases
        if self.connection_trials > 0:
            if not self.progress_dialog:
                self.progress_max = self.connection_trials
                self.progress_dialog = wx.ProgressDialog(
                    title=_('Connection progress'),
                    message=_('Connecting to the node...'),
                    maximum=self.progress_max + 1,
                    style=wx.GA_SMOOTH)
                self.progress_dialog.SetSizeHintsSz(self.progress_dialog.GetBestVirtualSize())
            else:
                self.connection_trials -= 1
                self.progress_dialog.Update(self.progress_max - self.connection_trials)
            wx.FutureCall(1000, self._TryConnect)
        else:
            # Connection failed
            self._DestroyProgress()
            self._SetWaiting(False)
            self.node_proxy = None
            self.statusbar.SetText(_("Not connected"))
            msg = _("Connection to the node has failed. \nPlease the check the node is running, then retry.")
            dialog = wx.MessageDialog(None, msg, caption=_("Connection error"), style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()

    def NodeKillSucceeded(self):
        """
        We managed to kill the (remote/local) node.
        """
        if self.alive:
            self.node_proxy = None
            self._SetWaiting(False)
            self.viewport.Disable()
            self.Redraw()
            self.statusbar.SetText(_("Not connected"))
        else:
            # If not alive, then we are in the quit phase
            self._Quit2()

    def NodeKillFailed(self):
        """
        The node refused to kill itself.
        """
        if self.alive:
            self.node_proxy = None
            self._SetWaiting(False)
            self.viewport.Disable()
            msg = _("You cannot kill this node.")
            dialog = wx.MessageDialog(None, msg, caption=_("Kill refused"), style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
        else:
            # If not alive, then we are in the quit phase
            self._Quit2()

    #===-----------------------------------------------------------------===#
    # Actions from the services
    #
    def SetServiceMenu(self, service_id, title, menu):
        """
        Allow a service to change the title of its entry in the
        main menu bar.
        """
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
