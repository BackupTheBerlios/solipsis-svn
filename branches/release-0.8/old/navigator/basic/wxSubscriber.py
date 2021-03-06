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
from solipsis.util.exception import InternalError
from solipsis.navigator.subscriber import AbstractSubscriber
from solipsis.navigator.basic.wxProcessor import WxProcessor
from solipsis.node.event import EventParser
import solipsis.navigator.basic.basicFrame 
import wx

# create event classes and event binder functions
NewPeerEvent, EVT_NEW_PEER       = wx.lib.newevent.NewEvent()
UpdatePeerEvent, EVT_UPDATE_PEER = wx.lib.newevent.NewEvent()
NodeInfoEvent, EVT_NODE_INFO     = wx.lib.newevent.NewEvent()
NodeCreationSuccess, EVT_NODE_CREATION_SUCCESS = wx.lib.newevent.NewEvent()
NodeCreationFailure, EVT_NODE_CREATION_FAILURE = wx.lib.newevent.NewEvent()



class WxSubscriber(wx.EvtHandler, AbstractSubscriber):
    """ Get node notifications and send wxEvents """

    def __init__(self, window):
        wx.EvtHandler.__init__(self)
        self.window = window
        self.eventProcessor  = WxProcessor(self.window)
        
         # Bind events to the related processor function
        self.Bind(EVT_NEW_PEER, self.eventProcessor.OnNewPeer)
        self.Bind(EVT_UPDATE_PEER, self.eventProcessor.OnUpdatePeer)
        self.Bind(EVT_NODE_INFO, self.eventProcessor.OnNodeInfo)
        self.Bind(EVT_NODE_CREATION_SUCCESS,
                  self.eventProcessor.OnNodeCreationSuccess)
        self.Bind(EVT_NODE_CREATION_FAILURE,
                  self.eventProcessor.OnNodeCreationFailure)
        
    def NEW(self, event):
        """ Reception of a NEW event from the node.
        
        Send a NewPeerEvent to the wxEventHandler  """
        
        parser = EventParser()
        peer = parser.createEntity(event)
        wxEvt = NewPeerEvent(peerinfo=peer)
            
        wx.PostEvent(self, wxEvt)
        

    def NODEINFO(self, event):
        """ Reception of a NODEINFO event from the node.
        Update the information related to my node
        """
        parser = EventParser()
        # Parse the event and create a Node object
        node = parser.createEntity(event)
        wxEvt = NodeInfoEvent(nodeinfo=node)
            
        wx.PostEvent(self, wxEvt)
        

    def OnNodeCreationFailure(self, reason):
        """ We are notified that an attempt to create a Node failed"""
        wxEvt = NodeCreationFailure(why=reason)
        wx.PostEvent(self, wxEvt)
        
    def _OnNodeCreationSuccess(self):
        """  We are notified that a node was successully created"""
        wxEvt = NodeCreationSuccess()
        wx.PostEvent(self, wxEvt)
        
