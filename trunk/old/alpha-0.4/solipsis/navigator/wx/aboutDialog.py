#Boa:Dialog:aboutDialog

from wxPython.wx import *

[wxID_ABOUTDIALOG, wxID_ABOUTDIALOGABOUTSTATICTEXT, 
 wxID_ABOUTDIALOGSOLIPSISURL, 
] = map(lambda _init_ctrls: wxNewId(), range(3))

class aboutDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_ABOUTDIALOG, name='aboutDialog',
              parent=prnt, pos=wxPoint(291, 110), size=wxSize(275, 143),
              style=wxDEFAULT_DIALOG_STYLE, title='About Solipsis')
        self._init_utils()
        self.SetClientSize(wxSize(280, 90))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the icon of the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)        
        
        self.aboutStaticText = wxStaticText(id=wxID_ABOUTDIALOGABOUTSTATICTEXT,
              label='You will find all information about Solipsis on :',
              name='aboutStaticText', parent=self, pos=wxPoint(10, 20),
              size=wxSize(250, 15), style=0)

        self.solipsisUrl = wxStaticText(id=wxID_ABOUTDIALOGABOUTSTATICTEXT,
              label='http://netofpeers.net',
              name='solipsisUrl', parent=self, pos=wxPoint(10, 50),
              size=wxSize(200, 15), style=0)
        
    def __init__(self, parent):
        self._init_ctrls(parent)
