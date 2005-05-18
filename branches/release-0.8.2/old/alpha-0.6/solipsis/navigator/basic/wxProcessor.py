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
