import wx

from solipsis.navigator.service import Service
from solipsis.util.exception import SolipsisException
#from solipsis.node.eventparser import EventParser
from solipsis.node.event import Event, EventParser
from solipsis.navigator.basic.image import ImageManager


class DuplicateChatterId(SolipsisException):
    pass

class Chat(Service):
    def __init__(self, connectionInfo):
        Service.__init__(self, Service.ID_CHAT,
                         'basic chat service', connectionInfo)
        self.chatters = {}
        self.connector = UDPConnector(ChatEventParser(), self.events, self.logger,
                                      connectionInfo)

    def enumerateChatters(self):
        return self.chatters.values()

    def addChatter(self, chatter):
        id = chatter.getId()
        if not self.chatters.has_key(id):
            self.chatters[id] = chatter
        else:
            raise DuplicateChatterId()

    def removeChatter(self, chatter):
        del self.chatters[chatter.getId()]

    def getChatter(self, id):
        return self.chatters[id]

    def broadcast(self, msg):
        """ Send a message to all chatters """
        for chatter in self.enumerateChatters():
            self.send(chatter.getId(), msg)

    def send(self, chatterId, msg):
        """ Send a message to a chatter """
        cnx = self.getChatter(chatterId).getConnectionInfo()
        self.socket.sendto(msg, cnx)

    def run(self):
        self.connector.start()

        while not self.isStopping:
            if not self.outgoing.empty():
                e = self.outgoing.get()
                self.connector.send(e)


class Chatter(object):
    def __init__(self, id, pseudo, connectionInfo):
        self.id = id
        self.pseudo = pseudo
        self.connectionInfo = connectionInfo

    def getId(self):
        return self.id

    def getPseudo(self):
        return self.pseudo

    def getConnectionInfo(self):
        return self.connectionInfo

class ChatEventParser(EventParser):
    def __init__(self, strEvent):
        self.strEvent = strEvent
        self.isParsed = False

    def createEvent(self, msg):
        """
        Returns: a ChatEvent object"""
        return ChatEvent(msg)

    def getData(self, event):
        return event.getArg('Message')

class ChatEvent(Event):
    def __init__(self, msg):
        self.setRequest('CHAT')
        self.addArg('Message',msg)


class WxChat(wx.Panel):
    def __init__(self,appli_window):
        wx.Panel.__init__(self, appli_window, -1)
        self.appli_window = appli_window

        [ wxID_WXMAINFRAMECHATTERSLISTBOX, wxID_WXMAINFRAMECHATTEXTCTRL,
          wxID_WXMAINFRAMEMESSAGETEXTCTRL, wxID_WXMAINFRAMESENDMESSAGEBUTTON
          ] = map(lambda _init_ctrls: wx.NewId(), range(4))

        [ wxID_WXMAINFRAMELOGO_WINDOW, wxID_WXMAINFRAMELOGOBITMAP
          ] = map(lambda _init_ctrls: wx.NewId(), range(2))

        self.logo_window = wx.Window(id=wxID_WXMAINFRAMELOGO_WINDOW,
                                     name='logo_window', parent=self,
                                     pos=wx.Point(0, 0),
                                     size=wx.Size(295, 76), style=0)

        logo = ImageManager.getBitmap(ImageManager.IMG_SOLIPSIS_LOGO)
        self.logoBitmap = wx.StaticBitmap(bitmap=logo,
                                          id=wxID_WXMAINFRAMELOGOBITMAP,
                                          name='logoBitmap', parent=self.logo_window,
                                          pos=wx.Point(0, 0), size=wx.Size(295, 76),
                                          style=0)

        self.logoHeight = 76
        self.chattersListBox = wx.ListBox(choices=[],
                                          id=wxID_WXMAINFRAMECHATTERSLISTBOX,
                                          name='chattersList',
                                          parent=self,
                                          pos=wx.Point(6, 30 + self.logoHeight),
                                          size=wx.Size(279,135),
                                          style=wx.NO_BORDER|wx.LB_ALWAYS_SB,
                                          validator=wx.DefaultValidator)

        self.chatTextCtrl = wx.TextCtrl(id=wxID_WXMAINFRAMECHATTEXTCTRL,
                                        name='chatTextCtrl',
                                        parent=self,
                                        pos=wx.Point(6, 201 + self.logoHeight),
                                        size=wx.Size(279, 233),
                                        style=wx.NO_BORDER|wx.TE_MULTILINE|wx.TE_READONLY,
                                        value='')

        self.messageTextCtrl = wx.TextCtrl(id=wxID_WXMAINFRAMEMESSAGETEXTCTRL,
                                           name='messageTextCtrl',
                                           parent=self,
                                           pos=wx.Point(6, 460 + self.logoHeight),
                                           size=wx.Size(279, 115),
                                           style=wx.NO_BORDER|wx.TE_MULTILINE,
                                           value='')

        sendBitmap =ImageManager.getBitmap(ImageManager.IMG_SEND_BLUE)
        self.sendMessageButton = wx.BitmapButton(bitmap=sendBitmap,
                                                 id=wxID_WXMAINFRAMESENDMESSAGEBUTTON,
                                                 name='sendMessageButton',
                                                 parent=self,
                                                 pos=wx.Point(190, 441 + self.logoHeight),
                                                 size=wx.Size(81, 17),
                                                 validator=wx.DefaultValidator)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.ClientDC(self)
        background = ImageManager.getBitmap(ImageManager.IMG_CHAT)
        dc.DrawBitmap(background, 0, self.logoHeight, True)

