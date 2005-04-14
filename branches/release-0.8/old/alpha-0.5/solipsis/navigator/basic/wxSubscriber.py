from solipsis.util.exception import SolipsisInternalError
from solipsis.navigator.subscriber import AbstractSubscriber
from solipsis.engine.event import EventParser
import solipsis.navigator.basic.basicFrame 
import wx

class WxSubscriber(AbstractSubscriber):
    """ Get node notifications and send wxEvents """

    def __init__(self, window):
        self.window = window
    
    def NEW(self, event):
        """ Reception of a NEW event from the node.
        
        Send a NewPeerEvent to the wxEventHandler  """
        
        parser = EventParser(event)
        info = parser.createEntity()
        wxEvt = solipsis.navigator.basic.basicFrame.NewPeerEvent(peerinfo=info)
            
        wx.PostEvent(self.window, wxEvt)
        

    def NODEINFO(self, event):
        """ Reception of a NODEINFO event from the node.
        Update the information related to my node
        """
        parser = EventParser(event)
        info = parser.createEntity()
        wxEvt = solipsis.navigator.basic.basicFrame.NodeInfoEvent(nodeinfo=info)
            
        wx.PostEvent(self.window, wxEvt)
        
