class WxProcessor:
    """ Process wxEvents """
    def __init__(self, window):
        """ Constructor.
        window : the window that instanciate this processor  """
        self._window = window

    def OnNewPeer(self, event):
        """ A new peer has been discovered
        event : the 'NewPeer' event """
        self._window.navigatorInfo.addPeerInfo(event.peerinfo)
        self._window.two_d_window.Refresh()
        
    def OnUpdatePeer(self, event):
        pass

    def OnNodeInfo(self, event):
        self._window.navigatorInfo.updateNodeInfo(event.nodeinfo)
        self._window.Refresh()
        self._window.navigatorInfo._isConnected = True
