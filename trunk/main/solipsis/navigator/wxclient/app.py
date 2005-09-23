# pylint: disable-msg=C0103,C0101
# Invalid name // too short name
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
"""
Specific navigator class which uses wx and displays the world in a 2D panel.
"""

import os
import sys
import wx
import wx.xrc
import bisect
from wx.xrc import XRCCTRL, XRCID

from solipsis.util.wxutils import _
from solipsis.util.wxutils import *        # '*' doesn't import '_'
from solipsis.util.urlhandlers import SetSolipsisURLHandlers
from solipsis.util.network import release_port
from solipsis.util.urls import SolipsisURL

from solipsis.services.wxcollector import WxServiceCollector
from solipsis.navigator.app import BaseNavigatorApp

from solipsis.navigator.wxclient.viewport import Viewport
from solipsis.navigator.wxclient.world import World
from solipsis.navigator.wxclient.statusbar import StatusBar
from solipsis.navigator.wxclient.network import NetworkLoop
from solipsis.navigator.wxclient.config import ConfigData

from solipsis.navigator.wxclient.BookmarksDialog import BookmarksDialog
from solipsis.navigator.wxclient.ConnectDialog import ConnectDialog
from solipsis.navigator.wxclient.PreferencesDialog import PreferencesDialog
from solipsis.navigator.wxclient.PositionJumpDialog import PositionJumpDialog



class NavigatorApp(BaseNavigatorApp, wx.App, XRCLoader):
    """
    Main application class. Derived from wxPython "wx.App".
    """

    def __init__(self, params, *args, **kargs):
        """available kargs: port"""
        BaseNavigatorApp.__init__(self, params, *args, **kargs)
        self.config_data = ConfigData(self.params)
        self.redraw_pending = False

        self.dialogs = None
        self.windows = None
        self.menubars = None
        # fields initialised by InitResources
        self.main_window = None
        self.main_menubar = None

        self.progress_dialog = None

        # Caution : wx.App.__init__ automatically calls OnInit(),
        # thus all data must be initialized before
        wx.App.__init__(self, *args, **kargs)

    def OnInit(self):
        """
        Main initialization handler.
        """
        self.InitWx()
        self.InitValidators()
        BaseNavigatorApp.OnInit(self)
        bookmarks_menu = self.main_menubar.GetMenu(
            self.main_menubar.FindMenu(_("&Bookmarks")))
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
        # 3. Other tasks are launched after ip found out & window is drawn
        wx.CallAfter(self.InitTwisted)
        wx.CallAfter(self.InitNetwork)
        return True

    def InitResources(self):
        """
        Load UI layout from XML file(s).
        """
        self.dialogs = []
        self.windows = ["main_window"]
        self.menubars = ["main_menubar"]
        objects = self.dialogs + self.windows + self.menubars
        self.LoadResource("resources/navigator.xrc")
        for obj_name in objects:
            self.__setattr__(obj_name, self.Resource(obj_name))
        # 2D viewport for the world view
        self.viewport_panel = XRCCTRL(self.main_window, "viewport_panel")
        self.viewport = Viewport(self.viewport_panel)
        self.world = World(self.viewport)
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

    def InitNetwork(self):
        """
        Launch network event loop.
        """
        self.network_loop = NetworkLoop(self.reactor, self)
        BaseNavigatorApp.InitNetwork(self)
        self.network_loop.start()
        self.network.StartURLListener(self.params.url_port_min,
                                      self.params.url_port_max)
        SetSolipsisURLHandlers()

    def InitServices(self):
        """
        Initialize all services.
        """
        self.services = WxServiceCollector(self.params, self.local_ip,
                                           self, self.reactor)
        BaseNavigatorApp.InitServices(self)
        # Service-specific menus in the menubar: We will insert
        # service menus just before the last menu, which is the "Help"
        # menu
        self.service_menus = []
        self.service_menu_pos = self.main_menubar.GetMenuCount() - 1
        # If the menu has become too wide because of the entries added
        # by services, resize main window so that the menu fits BUG:
        # this doesn't work :(
        self.main_menubar.Layout()
        self.main_window.Layout()
        self.main_window.SetSize(self.main_window.GetBestVirtualSize())

    def InitWx(self):
        """
        Initialize some basic wxWidgets stuff, including localization.
        """
        import locale as system_locale
        wx.InitAllImageHandlers()
        self.locale = wx.Locale()
        if not self.locale.Init2() \
               and wx.Platform not in ('__WXMSW__', '__WXMAC__'):
            print "Error: failed to initialize wx.Locale! " \
                "Please check the LC_MESSAGES " \
                "or LANG environment variable is properly set:"
            env_vars = os.environ.items()
            env_vars.sort()
            for name, value in env_vars:
                if name.startswith('LC_') or name.startswith('LANG'):
                    print "%s = %s" % (name, value)
            sys.exit(1)
        try:
            translation_dir = self.params.translation_dir
        except AttributeError:
            print "No translation dir specified in configuration file."
            pass
        else:
            self.locale.AddCatalogLookupPathPrefix(translation_dir)
            self.locale.AddCatalog("solipsis")
        # Workaround for buggy Python behaviour with floats
        system_locale.setlocale(system_locale.LC_NUMERIC, "C")
        # Override languages in config
        lang_code = self.locale.GetCanonicalName()
        if lang_code:
            self.config_data.languages = [str(lang_code.split('_')[0])]


    def InitValidators(self):
        """
        Setup validators for various form controls.
        Validators have two purposes :
        1. Validate proper data is entered in forms
        2. Transfer validated data to their storage location
           (an instance variable of a ManagedData subclass instance).
        """
        validators = [
            # [ Containing window, control name, validator class,
            #   data object, data attribute ]
            #~ [ self.prefs_dialog, "proxymode_auto", BooleanValidator,
            #~   c, "proxymode_auto" ],
        ]
        for v in validators:
            window, control_name, validator_class, data_obj, data_attr = v
            valid = validator_class(data_obj.Ref(data_attr))
            XRCCTRL(window, control_name).SetValidator(valid)

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
                    """clean viewport"""
                    self.redraw_pending = False
                    self.Redraw()
                self.future_call(t, _redraw)
                return True
        return False

    #
    # Helpers
    #
    def future_call(self, delay, function):
        """call function after delay (milli sec)"""
        wx.FutureCall(delay, function)

    def display_message(self, title, msg):
        """Way of communicta with user"""
        dialog = wx.MessageDialog(None, msg, caption=title,
                                  style=wx.OK | wx.ICON_EXCLAMATION)
        dialog.ShowModal()

    def display_warning(self, title, msg):
        """Way of communicta with user"""
        dialog = wx.MessageDialog(None, msg, caption=title,
                                  style=wx.OK | wx.ICON_WARNING)
        dialog.ShowModal()

    def display_error(self, title, msg):
        """Way of communicta with user"""
        dialog = wx.MessageDialog(None, msg, caption=title,
                                  style=wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()

    def display_status(self, msg):
        """report a status"""
        self.statusbar.SetText(msg)

    def _CallAfter(self, fun, *args, **kargs):
        """
        Call function asynchronously with args.
        """
        wx.CallAfter(fun, *args, **kargs)

    def _LaunchFirstDialog(self):
        """
        Display first UI dialog after everything has been initialized properly.
        """
        BaseNavigatorApp._LaunchFirstDialog(self)
        self._CallAfter(self._OpenConnectDialog)

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

    def _OpenConnectDialog(self):
        """get parameters of connection & connect"""
        connect_dialog = ConnectDialog(config_data=self.config_data,
                                       parent=self.main_window)
        if connect_dialog.ShowModal() != wx.ID_OK:
            return
        self.config_data.Compute()
        BaseNavigatorApp._OnConnect(self)

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

    #===-----------------------------------------------------------------===#
    # Event handlers for the main window
    # (in alphabetical order)
    #
    def _OnConnect(self, evt):
        """
        Called on "connect" event (menu -> File -> Connect).
        """
        self._OpenConnectDialog()

    def _OnDisplayAddress(self, evt=None):
        """
        Called on "node address" event (menu -> Actions -> Jump Near).
        """
        if self._CheckNodeProxy():
            address_str = self.world.GetNode().address.GetURL().ToString()
            clipboard = wx.TheClipboard
            clipboard.Open()
            clipboard.SetData(wx.TextDataObject(address_str))
            clipboard.Close()
            msg = _("Your address has been copied to the clipboard. \n"
                "If you paste it and send it to your friends, \n"
                "they will be able to jump near you in the Solipsis world.")
            msg += "\n" + _("For reminder, here is your address:") + " "
            msg += address_str
            dialog = wx.MessageDialog(self.main_window,
                message=msg,
                caption=_("Your Solipsis address"),
                style=wx.OK|wx.CENTRE|wx.ICON_INFORMATION
                )
            dialog.ShowModal()

    def _OnEditBookmarks(self, evt):
        """
        Called on "edit bookmarks" event (menu -> Bookmarks -> Edit bookmarks).
        """
        self.bookmarks_dialog.Show()
        self._SaveConfig()

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
                BaseNavigatorApp._OnJumpNear(self, v)

    def _OnJumpPos(self, evt):
        """
        Called on "jump to position" event (menu -> Actions -> Jump to position).
        """
        if not self._CheckNodeProxy():
            return
        jump_dialog = PositionJumpDialog(config_data=self.config_data,
                                         parent=self.main_window)
        if jump_dialog.ShowModal() == wx.ID_OK:
            x, y = jump_dialog.GetPosition()
            BaseNavigatorApp._OnJumpPos(self, (x, y))

    def OnPaint(self, event):
        """
        Called on repaint request.
        """
        self.viewport.Draw(onPaint=True)
        event.Skip()

    def _OnPreferences(self, evt):
        """
        Called on "preferences" event (menu -> File -> Preferences).
        """
        self.config_data.Compute()
        prefs_dialog = PreferencesDialog(config_data=self.config_data,
                                         parent=self.main_window)
        prefs_dialog.ShowModal()
        self._SaveConfig()

    def _Quit2(self):
        """
        The end of the quit procedure ;-)
        """
        BaseNavigatorApp._Quit2(self)
        # Process the last pending events
        self.ProcessPendingEvents()
        for obj_name in self.dialogs + self.windows:
            try:
                win = getattr(self, obj_name)
                win.Destroy()
            except:
                pass

    def OnResize(self, event):
        """
        Called on repaint request.
        """
        self.Redraw()

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
                    """action to perfome on right click"""
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
                self.progress_dialog.SetSizeHintsSz(
                    self.progress_dialog.GetBestVirtualSize())
            else:
                self.connection_trials -= 1
                self.progress_dialog.Update(
                    self.progress_max - self.connection_trials)
            self.future_call(3000, self._TryConnect)
        else:
            # Connection failed
            BaseNavigatorApp.NodeConnectionFailed(self, error)

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
        if pos == len(self.service_menus) \
               or self.service_menus[pos][1] != service_id:
            self.main_menubar.Insert(pos + self.service_menu_pos, menu, title)
            self.service_menus.insert(pos, val)
        else:
            self.main_menubar.Replace(pos + self.service_menu_pos, menu, title)
            self.service_menus[pos] = val

