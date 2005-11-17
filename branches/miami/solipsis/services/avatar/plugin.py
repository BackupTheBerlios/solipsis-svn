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
import socket
import wx
import random

from solipsis.util.compat import set
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import TwistedProxy, UIProxy
from solipsis.services.plugin import ServicePlugin

from gui import ConfigDialog
from network import NetworkLauncher
from repository import AvatarRepository, AcceptFilename
from cycling import CyclingAvatar


class Plugin(ServicePlugin):
    avatar_size_step = 12

    def Init(self, local_ip):
        self.avatars = AvatarRepository()
        self.reactor = self.service_api.GetReactor()
        self.host = local_ip
        self.port = 7780 + random.randrange(0, 100)

        # Network address container: { peer_id => (host, port) }
        self.hosts = {}
        self.node_avatar_hash = None
        self.node_id = None

        # Peers for which we have received an avatar hash but whose
        # address we don't know yet
        self.pending_peers = set()

        self.cycling_avatar = CyclingAvatar(self)

    def GetTitle(self):
        return _("Avatars")

    def GetDescription(self):
        return _("Exchange avatars to customize your appearance")

    def GetActions(self):
        return []

    def GetPointToPointActions(self):
        return []

    def DescribeService(self, service):
        service.address = "%s:%d" % (self.host, self.port)

    #
    # Here comes the real action
    #
    # FIXME: need to abstract action layer of plugins so that it does
    # not depend on navigator mode (in our case: netclient or
    # wxclient)
    def EnableBasic(self):
        """enable navigator-independant part"""
        # Set up network handler
        network = NetworkLauncher(self.reactor, self, self.port)
        self.network = TwistedProxy(network, self.reactor)
        # Start network
        self.network.Start()
        print "Avatar: enable"

    def Enable(self):
        """
        Enable the service.
        """
        # Set up avatar GUI
        dialog = ConfigDialog(self, self.service_api.GetDirectory())
        self.ui = UIProxy(dialog)
        # Set up main GUI hooks
        main_window = self.service_api.GetMainWindow()
        menu = wx.Menu()
        item_id = wx.NewId()
        menu.Append(item_id, _("&Configure"))
        wx.EVT_MENU(main_window, item_id, self.DisplayDialog)
        item_id = wx.NewId()
        menu.Append(item_id, "%s\tCtrl++" % _("Stretch avatars"))
        wx.EVT_MENU(main_window, item_id, self.StretchAvatars)
        item_id = wx.NewId()
        menu.Append(item_id, "%s\tCtrl+-" % _("Shrink avatars"))
        wx.EVT_MENU(main_window, item_id, self.ShrinkAvatars)
        self.service_api.SetMenu(_("Avatar"), menu)
        # Set up network handler
        network = NetworkLauncher(self.reactor, self, self.port)
        self.network = TwistedProxy(network, self.reactor)
        # Get saved config
        self._ApplyConfig()
        # Start network
        self.network.Start()

    def Disable(self):
        """
        Disable the service.
        """
        self.network.Stop()
        self.network = None
        self.ui.Destroy()
        self.ui = None

    def NewPeer(self, peer, service):
        """
        A new neighbour has appeared.
        """
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            pass
        else:
            self.hosts[peer.id_] = host, port
            # If we have an avatar, send its hash to our new neighbour
            if self.node_avatar_hash is not None:
                self.service_api.SendData(peer.id_, self.node_avatar_hash)
            # Use default avatar for now
            self.avatars.BindHashToPeer(None, peer.id_)
            # If we need to fetch the peer's avatar, do it
            if peer.id_ in self.pending_peers:
                self._LoadPeerAvatar(peer.id_)

    def ChangedPeer(self, peer, service):
        """
        One of our neighbours changed its information.
        """
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            if peer.id_ in self.hosts:
                del self.hosts[peer.id_]
        else:
            self.hosts[peer.id_] = host, port
            # If we need to fetch the peer's avatar, do it
            if peer.id_ in self.pending_peers:
                self._LoadPeerAvatar(peer.id_)

    def LostPeer(self, peer_id):
        """
        One of our neighbours has disappeared.
        """
        if peer_id in self.hosts:
            del self.hosts[peer_id]

    def ChangedNode(self, node):
        """
        The node has changed (also perhaps its ID).
        """
        self.node_id = node.id_
        self._ApplyConfig()
        if self.node_avatar_hash is not None:
            self.avatars.BindHashToPeer(self.node_avatar_hash, self.node_id)

    def DisplayDialog(self, evt=None):
        """
        Called when the "Configure" action is selected.
        """
        # The result of the Configure() method will be passed
        # to the callback, if successful.
        # This is because self.ui goes through an asynchronous proxy.
        def _configured(filename):
            self.service_api.SetConfig(filename)
            self._ApplyConfig()
        self.ui.Configure(callback=_configured)

    def StretchAvatars(self, evt=None):
        """
        Called when the "Stretch Avatars" action is selected.
        """
        s = self.avatars.GetProcessedAvatarSize()
        self.avatars.SetProcessedAvatarSize(s + self.avatar_size_step)

    def ShrinkAvatars(self, evt=None):
        """
        Called when the "Shrink Avatars" action is selected.
        """
        s = self.avatars.GetProcessedAvatarSize()
        if s > self.avatar_size_step:
            self.avatars.SetProcessedAvatarSize(s - self.avatar_size_step)

    def GotServiceData(self, peer_id, hash_):
        """
        Called when another peer sent its avatar hash.
        """
        if not self.avatars.BindHashToPeer(hash_, peer_id):
            if peer_id in self.hosts:
                self._LoadPeerAvatar(peer_id)
            else:
                self.pending_peers.add(peer_id)

    def SetNodeAvatar(self, filename):
        """
        Set our avatar to the given filename.
        """
        if filename is None:
            self.node_avatar_hash = None
            return
        try:
            data = file(filename, "rb").read()
        except (IOError, EOFError), e:
            print "Failed to load node avatar: '%s'" % str(e)
            return
        # Add the avatar to the repository, and send its hash to all our neighbours
        self.network.SetFile(filename)
        self.node_id = self.service_api.GetNode().id_
        self.node_avatar_hash = self.avatars.BindAvatarToPeer(data, self.node_id)
        for peer_id in self.hosts.keys():
            self.service_api.SendData(peer_id, self.node_avatar_hash)

    #
    # Private methods
    #
    def _ApplyConfig(self):
        """
        Apply configuration.
        """
        self.cycling_avatar.Stop()
        path = self.service_api.GetConfig()
        if path is not None:
            if os.path.isdir(path):
                #print "avatar is a directory..."
                avatars = []
                for filename in os.listdir(path):
                    if not AcceptFilename(filename):
                        continue
                    filepath = os.path.join(path, filename)
                    if not os.path.isfile(filepath):
                        continue
                    #print "-", filepath
                    avatars.append(filepath)
                if not avatars:
                    self.SetNodeAvatar(None)
                else:
                    self.cycling_avatar.SetAvatars(avatars)
                    self.cycling_avatar.Start()
            else:
                self.SetNodeAvatar(path)
        else:
            self.SetNodeAvatar(None)

    def _LoadPeerAvatar(self, peer_id):
        """
        Fetch the peer's avatar using its listening address.
        """
        def _got_avatar(data):
            """ Callback for success. """
            if peer_id in self.pending_peers:
                self.pending_peers.remove(peer_id)
            self.avatars.BindAvatarToPeer(data, peer_id)
        def _failed(error):
            """ Callback for failure. """
            print "failed getting avatar from '%s': %s" % (peer_id, str(error))
        host, port = self.hosts[peer_id]
        self.network.GetPeerFile(host, port, _got_avatar, _failed)

    def _ParseAddress(self, address):
        """
        Parse network address as supplied by a peer.
        Returns a (host, port) tuple.
        """
        try:
            t = address.split(':')
            if len(t) != 2:
                raise ValueError
            host = str(t[0]).strip()
            port = int(t[1])
            if not host:
                raise ValueError
            if port < 1 or port > 65535:
                raise ValueError
            return host, port
        except ValueError:
            #~ print "Wrong avatar address '%s'" % address
            raise
