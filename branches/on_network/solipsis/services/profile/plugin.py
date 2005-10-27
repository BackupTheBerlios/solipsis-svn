# pylint: disable-msg=C0103
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

import random
import wx

from solipsis.util.wxutils import _
from solipsis.services.plugin import ServicePlugin
from solipsis.services.profile import set_solipsis_dir
from solipsis.services.profile.message import display_message, display_status
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.facade import create_facade, get_facade
from solipsis.services.profile.filter_facade import \
     create_filter_facade, get_filter_facade
from solipsis.services.profile.network import NetworkManager
from solipsis.services.profile.view import EditorView, ViewerView, FilterView
from solipsis.services.profile.gui.EditorFrame import EditorFrame
from solipsis.services.profile.gui.ViewerFrame import ViewerFrame
from solipsis.services.profile.gui.FilterFrame import FilterFrame


class ClassAttribute(object):
    """Make a class attribute"""
    def __init__(self):
        self.value = None
        
    def __get__(self, inst, objtype):
        return self.value
        
    def __set__(self, inst, value):
        self.value = value
        
class Plugin(ServicePlugin):
    """This the working class for services plugins."""
    
    # Define 'service_api' as a CLASS attribute
    service_api = ClassAttribute()
    
    def Init(self, local_ip):
        """
        This method does any kind of concrete initialization stuff,
        rather than doing it in __init__.  Especially, the service_api
        must *not* be used in __init__, since all data relating to the
        plugin may not have been initialized on the API side.
        """
        self.host = local_ip
        self.port = random.randrange(7000, 7100)
        self.network = None
        self.editor_frame = None
        self.viewer_frame = None
        self.filter_frame = None
        self.peer_services = {}
        # declare actions
        self.MAIN_ACTION = {_("Edit Profile..."): self.modify_profile,
                            _("Filter Profiles..."): self.filter_profile,
                            }
        self.POINT_ACTIONS = {#"View all...": self.show_profile,
                              _("View profile..."): self.get_profile,
                              _("View blog..."): self.get_blog_file,
                              _("Get files..."): self.select_files,}

    # Service setup

    # FIXME: need to abstract action layer of plugins so that it does
    # not depend on navigator mode (in our case: netclient or
    # wxclient)
    def EnableBasic(self):
        """enable non graphic part"""
        set_solipsis_dir(self.service_api.GetDirectory())
        self.network = NetworkManager()
        self.activate(True)
        
    def Enable(self):
        """
        All real actions involved in initializing the service should
        be defined here, not in the constructor.  This includes
        e.g. opening sockets, collecting data from directories, etc.
        """
        set_solipsis_dir(self.service_api.GetDirectory())
        # init windows
        main_window = self.service_api.GetMainWindow()
        options = {}
        options["standalone"] = False
        self.editor_frame = EditorFrame(options, main_window, -1, "",
                                          plugin=self)
        self.viewer_frame = ViewerFrame(options, main_window, -1, "",
                                          plugin=self)
        self.filter_frame = FilterFrame(options, main_window, -1, "",
                                          plugin=self)
        # Set up main GUI hooks
        menu = wx.Menu()
        for action, method in self.MAIN_ACTION.iteritems():
            item_id = wx.NewId()
            menu.Append(item_id, _(action))
            wx.EVT_MENU(main_window, item_id, method)
        self.service_api.SetMenu(self.GetTitle(), menu)
        # launch network
        self.network = NetworkManager(download_dlg=self.editor_frame.download_dlg)
        self.activate(True)
    
    def Disable(self):
        """It is called when the user chooses to disable the service."""
        # ask for saving (ca not simply call Close() on editor frame
        # method because of multithreading and the frame is destroyed
        # before the user actually answer to the popup
        if self.editor_frame and self.editor_frame.modified:
            self.editor_frame.do_modified(False)
            dlg = wx.MessageDialog(
                self.editor_frame,
                'Your profile has been modified. Do you want to save it?',
                'Saving Profile',
                wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_YES:
                get_facade()._desc.save()
        if self.filter_frame and self.filter_frame.modified:
            self.filter_frame.do_modified(False)
            dlg = wx.MessageDialog(
                self.filter_frame,
                'Your filters have been modified. Do you want to save them?',
                'Saving Filters',
                wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_YES:
                get_filter_facade().save()
        self.activate(False)

    def activate(self, active=True):
        """eable/disable service"""
        if not active:
            self.network.stop()
            self.network.server.stop_listening()
            for peer_id in self.peer_services.keys():
                self.LostPeer(peer_id)
        else:
            self.network.start()
            self.network.server.start_listening()
            for peer_id in self.peer_services.keys():
                self.NewPeer(*self.peer_services[peer_id])

    # Service methods
    def modify_profile(self, evt):
        """display profile once loaded"""
        if not self.editor_frame is None:
            self.editor_frame.Show()
            
    def filter_profile(self, evt):
        """display profile once loaded"""
        if self.filter_frame:
            self.filter_frame.Show()
            
#     def show_profile(self, evt):
#         """display profile once loaded"""
#         if self.viewer_frame:
#             self.viewer_frame.Show()

    def get_profile(self, peer_id, deferred=None):
        """request downwload of profile"""
        on_done = self.network.get_profile(peer_id)
        if on_done != None:
            on_done.addCallback(self._on_new_profile, peer_id)
            deferred and on_done.chainDeferred(deferred)

    def get_blog_file(self, peer_id, deferred=None):
        """request downwload of blog"""
        on_done = self.network.get_blog_file(peer_id)
        if on_done != None:
            on_done.addCallback(self._on_new_blog, peer_id)
            deferred and on_done.chainDeferred(deferred)

    def select_files(self, peer_id, deferred=None):
        """request downwload of list of shared files"""
        on_done = self.network.get_shared_files(peer_id)
        if on_done != None:
            on_done.addCallback(self._on_shared_files, peer_id)
            deferred and on_done.chainDeferred(deferred)

    # side method
    def get_files(self, peer_id, file_descriptors):
        """request downwload of given files"""
        if self.editor_frame and get_prefs("display_dl"):
            self.editor_frame.download_dlg.init()
            self.editor_frame.download_dlg.Show()
        deferred = self.network.get_files(peer_id, file_descriptors,
                                          self._on_all_files)
        deferred and deferred.addCallback(
            lambda file_name: "%s downloaded\n"% file_name)

    # callbacks methods
    def _on_new_profile(self, document, peer_id):
        """store and display file object corresponding to profile"""
        get_facade().fill_data(peer_id, document)
        return str(document)
            
    def _on_new_blog(self, blog, peer_id):
        """store and display file object corresponding to blog"""
        get_facade().fill_blog(peer_id, blog)
        return str(blog)
    
    def _on_shared_files(self, files, peer_id):
        """store and display file object corresponding to blog"""
        get_facade().fill_shared_files(peer_id, files)
        return str(files)
    
    def _on_all_files(self):
        """store and display file object corresponding to blog"""
        if self.editor_frame:
            self.editor_frame.download_dlg.complete_all_files()
        else:
            print 'No more file to download'

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
    def DoAction(self, it, deferred=None):
        """Called when the general action is invoked, if available."""
        # retreive corect method
        actions = self.MAIN_ACTION.values()
        # call method on peer
        actions[it](deferred)

    def DoPointToPointAction(self, it, peer, deferred=None):
        """Called when a point-to-point action is invoked, if available."""
        if get_facade() and get_facade()._activated:
            # retreive corect method
            actions = self.POINT_ACTIONS.values()
            # call method on peer
            actions[it](peer.id_, deferred)
        # service not activated, do nothing
        else:
            print "service not activated"
            

    # Peer management
    # FIXME: check really need to call network method
    def NewPeer(self, peer, service):
        """delegate to network"""
        self.peer_services[peer.id_] = (peer, service)
        if get_facade() and get_facade()._activated:
            self.network.on_new_peer(peer)

    def ChangedPeer(self, peer, service):
        """delegate to network"""
        self.peer_services[peer.id_] = (peer, service)
        if get_facade() and get_facade()._activated:
            self.network.on_change_peer(peer, service)

    def LostPeer(self, peer_id):
        """delegate to network"""
        del self.peer_services[peer_id]
        if get_facade() and get_facade()._activated:
            self.network.on_lost_peer(peer_id)
            get_facade().set_connected(peer_id, False)

    def GotServiceData(self, peer_id, data):
        """delegate to network"""
        if get_facade() and get_facade()._activated:
            self.network.on_service_data(peer_id, data)

    def ChangedNode(self, node):
        """need to update node_id"""
        # ChangedNode is call more than one time on change. Thus, be
        # careful not to do the job every time
        if get_facade() is None or get_facade()._desc.document.get_pseudo() != node.pseudo:
            # creation
            facade = create_facade(node.id_)
            filter_facade = create_filter_facade(node.id_)
            if not facade.load():
                display_status(_("You have no profile yet for pseudo %s"% node.pseudo))
# ChangedNode called too many times at startup and make this popup appear several times => bother
# Replace by display_status for now
#                 display_message(
#                     _(u"You have no profile yet for pseudo %s.\n\n "
#                       "You may create one clicking on the menu Profile, "
#                       "and selecting 'Modify Profile'"% node.pseudo),
#                     title=_("New profile"))
            if not filter_facade.load():
                display_status(_("You have no filters defined yet for pseudo %s"% node.pseudo))
# ChangedNode called too many times at startup and make this popup appear several times => bother
# Replace by display_status for now
#                 display_message(
#                     _(u"You have no filters defined yet for pseudo %s.\n\n Filters are used "
#                       "to match your neighbors' profile and alert you if they "
#                       "match with your criteria.\n\n"
#                       "You may create your filters by clicking on the menu 'Profile', "
#                       "and selecting 'Filter Profiles'"% node.pseudo),
#                     title=_("New filters"))
            facade.change_pseudo(node.pseudo)
            # updating views
            if self.editor_frame:
                facade.add_view(EditorView(facade._desc,
                                           self.editor_frame))
                self.editor_frame.on_change_facade()
                facade.add_view(ViewerView(facade._desc,
                                           self.viewer_frame))
                self.viewer_frame.on_change_facade()
            if self.filter_frame:
                filter_facade.add_view(FilterView(filter_facade._desc,
                                                  self.filter_frame))
                self.filter_frame.on_change_facade()
            display_status(_("Loaded data for %s"% node.pseudo))
