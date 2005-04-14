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
## -----                           addFlagDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for adding a new Flag.
##
## ******************************************************************************

from wxPython.wx import *
import os
import commun

def create(parent):
    return addFlagDialog(parent)

[wxID_ADDFLAGDIALOG, wxID_ADDFLAGDIALOGNAMESTATICTEXT,
 wxID_ADDFLAGDIALOGNAMETEXTCTRL,
] = map(lambda _init_ctrls: wxNewId(), range(3))

class addFlagDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_ADDFLAGDIALOG,
              name='addFlagDialog', parent=prnt, pos=wxPoint(0, 0),
              size=wxSize(184, 173), style=wxDEFAULT_DIALOG_STYLE,
              title='Add Flag')
        self._init_utils()
        self.SetClientSize(wxSize(230, 120))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the icon of the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.nameStaticText = wxStaticText(id=wxID_ADDFLAGDIALOGNAMESTATICTEXT,
              label='Flag name :', name='nameStaticText', parent=self,
              pos=wxPoint(10, 20), size=wxSize(74, 15), style=0)

        self.nameTextCtrl = wxTextCtrl(id=wxID_ADDFLAGDIALOGNAMETEXTCTRL,
              name='nameTextCtrl', parent=self, pos=wxPoint(90, 20),
              size=wxSize(105, 21), style=0, value='')

        self.okButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_ok_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_OK, name='okButton', parent=self,
              pos=wxPoint(10, 80), size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.cancelButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_cancel_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CANCEL, name='cancelButton',
              parent=self, pos=wxPoint(140, 80), size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        EVT_BUTTON(self.okButton, wxID_OK, self.OnOkButton)

    def __init__(self, parent, navigator):

        # navigator
        self.navigator = navigator

        self._init_ctrls(parent)

    def OnOkButton(self, event):
        """ save the flag with the name filled by the user """

        # get the flag parameters
        name = self.nameTextCtrl.GetValue()
        posX = self.navigator.getNodePosX()
        posY = self.navigator.getNodePosY()

        # errors control
        if name == "":
            commun.displayError(self, "Your flag name is empty !")
        elif posX == "":
            commun.displayError(self, "Your flag X coordinate is empty !")
        elif posY == "":
            commun.displayError(self, "Your flag Y coordinate is empty !")
        else:
            flagFile = commun.FLAG_DIR_NAME + os.sep + name

            # control the doublon
            if os.path.isfile(flagFile):
                commun.displayError(self, "This flag name already exists. Please, choose another name.")
                return 0

            # open the flag file
            try:
                f = file(flagFile, 'w')
            except:
                commun.displayError(self, 'Can not open the file %s' %flagFile)
                return 0

            # save the parameters in the flag file
            line = name + ';' + str(posX) + ';'+ str(posY)
            f.write(line)
            f.close()

            # close the dialog box
            self.Close(FALSE)
