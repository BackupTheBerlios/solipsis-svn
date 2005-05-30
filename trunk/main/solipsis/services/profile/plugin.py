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
"""main class for plugin. Allow 'plug&Play' into navigator"""

import socket
import random
import wx
import os

from StringIO import StringIO

from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxy
from solipsis.services.plugin import ServicePlugin
from solipsis.services.profile import PROFILE_DIR, PROFILE_FILE, KNOWN_PORT
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.network import NetworkManager
from solipsis.services.profile.document import CacheDocument, FileDocument
from solipsis.services.profile.view import GuiView, HtmlView, PrintView
from solipsis.services.profile.gui.ProfileFrame import ProfileFrame

      
class Plugin(ServicePlugin):
    """This the working class for services plugins."""

    
    def Init(self):
        """
        This method does any kind of concrete initialization stuff,
        rather than doing it in __init__.  Especially, the service_api
        must *not* be used in __init__, since all data relating to the
        plugin may not have been initialized on the API side.
        """
        # TODO: smartly discover our own address IP
        # (this is where duplicated code starts to appear...)
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = random.randrange(7000, 7100)
        self.network = NetworkManager(self.host,  random.randrange(7100, 7200),
                                      self.service_api, get_facade())
        # init facade. Views will be initialized in Enable
        # (views depend on graphical mode)
        self.facade = get_facade()
        self.profile_frame = None
        # declare actions
        self.MAIN_ACTION = {"Modify ...": self.show_profile,
                            }
        self.POINT_ACTIONS = {"Get profile": self.get_profile,
                              "Get blog": self.get_blog_file,
                              "Get files...": self.select_files,
                              }

    # Service setup

    # FIXME: need to abstract action layer of plugins so that it does
    # not depend on navigator mode (in our case: netclient or
    # wxclient)
    def EnableBasic(self):
        """enable non graphic part"""
        # TODO: expose interface of facade to netClient
        # create views & doc
        file_doc = FileDocument()
        file_doc.load(os.path.join(PROFILE_DIR, PROFILE_FILE))
        cache_doc = CacheDocument()
        cache_doc.import_document(file_doc)
        print_view = PrintView(cache_doc)
        self.facade.add_document(cache_doc)
        self.facade.add_view(print_view)
        # launch network
        self.network.start_listening()
        
    def Enable(self):
        """
        All real actions involved in initializing the service should
        be defined here, not in the constructor.  This includes
        e.g. opening sockets, collecting data from directories, etc.
        """
        # init windows
        main_window = self.service_api.GetMainWindow()
        self.profile_frame = ProfileFrame(False, main_window, -1, "")
        # create views & doc
        file_doc = FileDocument()
        file_doc.load(os.path.join(PROFILE_DIR, PROFILE_FILE))
        cache_doc = CacheDocument()
        cache_doc.import_document(file_doc)
        gui_view = UIProxy(GuiView(cache_doc, self.profile_frame))
        html_view = HtmlView(cache_doc,
                             self.profile_frame.preview_tab.html_preview,
                             True)
        self.facade.add_document(file_doc)
        self.facade.add_document(cache_doc)
        self.facade.add_view(gui_view)
        self.facade.add_view(html_view)
        self.facade.refresh_html_preview()
        # Set up main GUI hooks
        menu = wx.Menu()
        for action, method in self.MAIN_ACTION.iteritems():
            item_id = wx.NewId()
            menu.Append(item_id, _(action))
            def _clicked(event):
                """call profile from main menu"""
                method()
            wx.EVT_MENU(main_window, item_id, _clicked)
        self.service_api.SetMenu(self.GetTitle(), menu)
        # launch network
        self.network.start_listening()
    
    def Disable(self):
        """It is called when the user chooses to disable the service."""
        self.facade.save_profile(os.path.join(PROFILE_DIR, PROFILE_FILE))
        self.network.stop_listening()

    # Service methods
    def show_profile(self):
        if self.profile_frame:
            self.profile_frame.Show()

    def _on_new_profile(self, document):
        """store and display file object corresponding to profile"""
        print "downloaded profile", document.get_pseudo()
        self.facade.fill_data((document.get_pseudo(), document))
    
    def _on_new_blog(self, blog):
        """store and display file object corresponding to blog"""
        self.facade.fill_blog((blog.owner, blog))

    def get_profile(self, peer_id):
        self.network.get_profile(peer_id, self._on_new_profile)

    def get_blog_file(self, peer_id):
        self.network.get_blog_file(peer_id, self._on_new_blog)

    def get_files(self, peer_id, file_names):
        self.network.get_file(peer_id, file_names)

    def select_files(self, peer_id):
        # get profile
        # display dialog to select files
        pass

    # Service description methods
    def GetTitle(self):
        """Returns a short title of the plugin."""
        return _("Profile")

    def GetDescription(self):
        """Returns a short description of the plugin. """
        return _("Manage personal information and share it with people")

    def GetActions(self):
        """Returns an array of strings advertising possible actions
        with all peers, or None if no such action is allowed.
        """
        return [_(desc) for desc in self.MAIN_ACTION]

    def GetPointToPointActions(self):
        """Returns an array of strings advertising point-to-point
        actions with another peer, or None if point-to-point actions
        are not allowed.
        """
        return [_(desc) for desc in self.POINT_ACTIONS]

    def DescribeService(self, service):
        """
        Fills the Service object used to describe the service to other peers.
        """
        service.address = "%s:%d" % (self.host, self.port)

    # UI event responses
    def DoAction(self, it):
        """Called when the general action is invoked, if available."""
        raise NotImplementedError

    def DoPointToPointAction(self, it, peer):
        """Called when a point-to-point action is invoked, if available."""
        if self.facade.is_activated():
            # retreive corect method
            actions = self.POINT_ACTIONS.values()
            # call method on peer
            actions[it](peer.id_)
        # service not activated, do nothing
        else:
            print "service not activated"
            

    # Peer management
    # FIXME: reactivate when efficient
    def NewPeer(self, peer, service):
        """delegate to network"""
        if self.facade.is_activated():
            self.network.on_new_peer(peer, service)

    def ChangedPeer(self, peer, service):
        """delegate to network"""
        if self.facade.is_activated():
            self.network.on_change_peer(peer, service)

    def LostPeer(self, peer_id):
        """delegate to network"""
        if self.facade.is_activated():
            self.network.on_lost_peer(peer_id)

    def GotServiceData(self, peer_id, data):
        """delegate to network"""
        if self.facade.is_activated():
            self.network.on_service_data(peer_id, data)

    def ChangedNode(self, node):
        # new IP ? what consequence on network?
        pass
