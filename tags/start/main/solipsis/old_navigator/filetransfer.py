import wx
from solipsis.navigator.basic.image import ImageManager

class WxFileTransfer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        [ wxID_WXMAINFRAMELOGO_WINDOW, wxID_WXMAINFRAMELOGOBITMAP
          ] = map(lambda _init_ctrls: wx.NewId(), range(2))

        self.logo_window = wx.Window(id=wxID_WXMAINFRAMELOGO_WINDOW,
                                     name='logo_window', parent=self, pos=wx.Point(0, 0),
                                     size=wx.Size(295, 76), style=0)
        
        logo = ImageManager.getBitmap(ImageManager.IMG_SOLIPSIS_LOGO)
        self.logoBitmap = wx.StaticBitmap(bitmap=logo,
                                          id=wxID_WXMAINFRAMELOGOBITMAP,
                                          name='logoBitmap', parent=self.logo_window,
                                          pos=wx.Point(0, 0), size=wx.Size(295, 76),
                                          style=0)

        button = wx.Button(self, -1, 'I do nothing')
