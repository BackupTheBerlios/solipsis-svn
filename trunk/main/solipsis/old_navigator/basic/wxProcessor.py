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
class WxProcessor(object):
    """ Process solipsis custom wxEvents """
    def __init__(self, window):
        """ Constructor.
        window : the window that instanciated this processor  """
        self.window = window

    def OnNewPeer(self, event):
        """ A new peer has been discovered
        event : the 'NewPeer' event """
        self.window.navigatorInfo.addPeerInfo(event.peerinfo)
        self.window.two_d_window.Refresh()

    def OnUpdatePeer(self, event):
        pass

    def OnNodeInfo(self, event):
        self.window.navigatorInfo.updateNodeInfo(event.nodeinfo)
        self.window.Refresh()
        self.window.navigatorInfo._isConnected = True

    def OnNodeCreationFailure(self, event):
        """ We are notified that an attempt to create a Node failed"""
        # create a popup error dialog
        reason = event.why
        self.window.entityDialog.OnNodeCreationFailure(reason)


    def OnNodeCreationSuccess(self, event):
        """  We are notified that a node was successully created"""
        # refresh the entity dialog box to display this node
        self.window.entityDialog.OnNodeCreationSuccess()
