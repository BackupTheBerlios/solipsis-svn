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
## -----                           newLocalNodeDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for starting a new local
##   entity on his machine.
##
## ******************************************************************************

from wxPython.wx import *

def create(parent):
    return newLocalNodeDialog(parent)

[wxID_NEWLOCALNODEDIALOG, wxID_NEWLOCALNODEDIALOGCANCELBUTTON,
 wxID_NEWLOCALNODEDIALOGOKBUTTON, wxID_NEWLOCALNODEDIALOGPSEUDOSTATICTEXT,
 wxID_NEWLOCALNODEDIALOGPSEUDOTEXTCTRL,
] = map(lambda _init_ctrls: wxNewId(), range(5))

class newLocalNodeDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_NEWLOCALNODEDIALOG,
              name='newLocalNodeDialog', parent=prnt, pos=wxPoint(0, 0),
              size=wxSize(184, 173), style=wxDEFAULT_DIALOG_STYLE,
              title='New node')
        self._init_utils()
        self.SetClientSize(wxSize(230, 120))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the icon of the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.pseudoStaticText = wxStaticText(id=wxID_NEWLOCALNODEDIALOGPSEUDOSTATICTEXT,
              label='Node pseudo :', name='pseudoStaticText', parent=self,
              pos=wxPoint(10, 20), size=wxSize(80, 15), style=0)

        self.pseudoTextCtrl = wxTextCtrl(id=wxID_NEWLOCALNODEDIALOGPSEUDOTEXTCTRL,
              name='pseudoTextCtrl', parent=self, pos=wxPoint(100, 20),
              size=wxSize(100, 21), style=0, value='')

        self.okButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_ok_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_OK, name='okButton', parent=self,
              pos=wxPoint(10, 80), size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.cancelButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_cancel_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CANCEL, name='cancelButton',
              parent=self, pos=wxPoint(140, 80), size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

    def __init__(self, parent):
        self._init_ctrls(parent)
