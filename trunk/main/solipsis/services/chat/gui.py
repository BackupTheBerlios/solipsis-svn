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

import os, os.path
import md5
import sys
import wx
from wx.xrc import XRCCTRL, XRCID

from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.util.wxutils import _
from solipsis.util.wxutils import *        # '*' doesn't import '_'

class ChatWindow(wx.EvtHandler, XRCLoader, UIProxyReceiver):
    def __init__(self, plugin, dir):
        self.plugin = plugin
        self.pseudos = {}

        wx.EvtHandler.__init__(self)
        UIProxyReceiver.__init__(self)

        # Load widgets from resource file
        self.windows = ["chat_window"]
        objects = self.windows

        self.LoadResource(os.path.join(dir, "gui.xrc"))
        for obj_name in objects:
            setattr(self, obj_name, self.Resource(obj_name))
        
        # Shortcuts to objects
        self.chat_view = XRCCTRL(self.chat_window, "chat_view")
        self.chat_edit = XRCCTRL(self.chat_window, "chat_edit")
        self.chat_users = XRCCTRL(self.chat_window, "chat_users")
        
        self.chat_users.InsertColumn(0, _("Nickname"))

        # Nicer sizing
        for obj_name in objects:
            attr = getattr(self, obj_name)
            attr.SetSizeHintsSz(attr.GetBestVirtualSize())

        # UI event handlers
        wx.EVT_BUTTON(self.chat_window, XRCID("chat_send"), self._Send)
        wx.EVT_BUTTON(self.chat_window, XRCID("chat_close"), self._Close)
        wx.EVT_CLOSE(self.chat_window, self._Close)


    def AppendMessage(self, peer_id, message, our_message=False):
        """
        Append a formatted message to the text window.
        """
        message = message.strip()
        if message:
            self.chat_window.Show()
            self.chat_window.Raise()
            style = self.chat_view.GetDefaultStyle()
            font = style.GetFont()
            old_colour = style.GetTextColour()
            if our_message:
                style.SetTextColour(wx.BLUE)
            # Display pseudo in bold
            font.SetWeight(wx.BOLD)
            style.SetFont(font)
            self.chat_view.SetDefaultStyle(style)
            pseudo = self.pseudos.get(peer_id, '???')
            self.chat_view.AppendText('[%s] ' % pseudo)
            # Display message in regular weight
            font.SetWeight(wx.NORMAL)
            style.SetFont(font)
            self.chat_view.SetDefaultStyle(style)
            self.chat_view.AppendText(message + "\n")
            # Restore default style
            style.SetTextColour(wx.NullColour)
            self.chat_view.SetDefaultStyle(style)
    
    def AppendSelfMessage(self, peer_id, message):
        """
        Append a formatted message to the text window.
        """
        self.AppendMessage(peer_id, message, True)
    
    def AddPeer(self, peer):
        if peer.pseudo:
            self.pseudos[peer.id_] = peer.pseudo
            index = self.chat_users.GetItemCount()
            self.chat_users.InsertStringItem(index, peer.pseudo)
            self.chat_users.SetItemData(index, self._PeerData(peer.id_))

    def RemovePeer(self, peer_id):
        index = self.chat_users.FindItemData(0, self._PeerData(peer_id))
        print index
        self.chat_users.DeleteItem(index)
    
    def UpdatePeer(self, peer):
        self.RemovePeer(peer.id_)
        self.AddPeer(peer)

    def Destroy(self):
        """
        Destroy chat interface.
        """
        self.chat_window.Destroy()
    
    def Show(self):
        """
        Show chat interface.
        """
        self.chat_window.Show()
        self.chat_window.Raise()
        self.chat_edit.SetFocus()

    def _PeerData(self, peer_id):
        hash = 0
        for x in md5.new(peer_id).digest():
            hash = (hash << 8) + ord(x)
        return int(hash & sys.maxint)

    def _Close(self, evt):
        """
        Called on window close event.
        """
        self.chat_window.Hide()

    def _Send(self, evt):
        """
        Called on "Send" button event.
        """
        text = self.chat_edit.GetValue().strip()
        self.chat_edit.Clear()
        if len(text):
            self.plugin.SendMessage(text)
