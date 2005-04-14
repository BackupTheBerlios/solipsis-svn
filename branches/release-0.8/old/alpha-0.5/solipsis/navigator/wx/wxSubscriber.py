from solipsis.util.exception import SolipsisInternalError
from solipsis.navigator.subscriber import AbstractSubscriber
import wx

class WxSubscriber(AbstractSubscriber):
    """ Get node notification and send wxEvents """
    def NEW(self, event):
        p = Peer()
        p.setAddress = event.getAddress()
        evt = NewPeerEvent(peer=p)
            
        wx.PostEvent(evt)
        

    
