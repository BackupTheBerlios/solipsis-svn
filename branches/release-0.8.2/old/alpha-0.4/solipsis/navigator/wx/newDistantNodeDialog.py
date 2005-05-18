#!/usr/local/bin/env python
######################################

## SOLIPSIS Copyright (C) France Telecom

## This file is part of SOLIPSIS.

##    SOLIPSIS is free software; you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as published by
##    the Free Software Foundation; either version 2.1 of the License, or
##    (at your option) any later version.

##    SOLIPSIS is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU Lesser General Public License for more details.

##    You should have received a copy of the GNU Lesser General Public License
##    along with SOLIPSIS; if not, write to the Free Software
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

## ------------------------------------------------------------------------------
## -----                           newDistantNodeDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for adding a new distant entity
##   to his list.
##
## ******************************************************************************

from wxPython.wx import *

def create(parent):
    return newDistantNodeDialog(parent)

[wxID_NEWDISTANTNODEDIALOG,
 wxID_NEWDISTANTNODEDIALOGHOSTNODETEXT, wxID_NEWDISTANTNODEDIALOGHOSTTEXTCTRL,
 wxID_NEWDISTANTNODEDIALOGPORTNODETEXT, wxID_NEWDISTANTNODEDIALOGPORTTEXTCTRL,
] = map(lambda _init_ctrls: wxNewId(), range(5))

class newDistantNodeDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_NEWDISTANTNODEDIALOG,
              name='newDistantNodeDialog', parent=prnt, pos=wxPoint(0, 0),
              size=wxSize(311, 203), style=wxDEFAULT_DIALOG_STYLE,
              title='New node')
        self._init_utils()
        self.SetClientSize(wxSize(230, 180))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the icon of the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.hostNodeText = wxStaticText(id=wxID_NEWDISTANTNODEDIALOGHOSTNODETEXT,
              label='Node host :', name='hostNodeText', parent=self,
              pos=wxPoint(10, 20), size=wxSize(55, 13), style=0)

        self.portNodeText = wxStaticText(id=wxID_NEWDISTANTNODEDIALOGPORTNODETEXT,
              label='Node port :', name='portNodeText', parent=self,
              pos=wxPoint(10, 80), size=wxSize(53, 13), style=0)

        self.hostTextCtrl = wxTextCtrl(id=wxID_NEWDISTANTNODEDIALOGHOSTTEXTCTRL,
              name='hostTextCtrl', parent=self, pos=wxPoint(70, 20),
              size=wxSize(100, 21), style=0, value='')

        self.portTextCtrl = wxTextCtrl(id=wxID_NEWDISTANTNODEDIALOGPORTTEXTCTRL,
              name='portTextCtrl', parent=self, pos=wxPoint(70, 80),
              size=wxSize(100, 21), style=0, value='')

        self.okButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_ok_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_OK,
              name='okButton', parent=self, pos=wxPoint(10, 130),
              size=wxSize(78, 39), style=0,
              validator=wxDefaultValidator)

        self.cancelButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_cancel_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CANCEL,
              name='cancelButton', parent=self, pos=wxPoint(140, 130),
              size=wxSize(78, 39), style=0,
              validator=wxDefaultValidator)

    def __init__(self, parent):
        self._init_ctrls(parent)
