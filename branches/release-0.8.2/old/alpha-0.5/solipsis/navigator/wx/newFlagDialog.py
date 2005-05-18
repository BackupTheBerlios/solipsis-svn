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
## -----                           newFlagDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for new flag creation or
##   modification.
##
## ******************************************************************************

from wxPython.wx import *
import os
from solipsis.navigator.wx.guiMessage import displayError


def create(parent):
    return newFlagDialog(parent)

[wxID_NEWFLAGDIALOG, wxID_NEWFLAGDIALOGNAMESTATICTEXT,
 wxID_NEWFLAGDIALOGNAMETEXTCTRL, wxID_NEWFLAGDIALOGXPOSSTATICTEXT,
 wxID_NEWFLAGDIALOGXPOSTEXTCTRL, wxID_NEWFLAGDIALOGYPOSSTATICTEXT,
 wxID_NEWFLAGDIALOGYPOSTEXTCTRL,
] = map(lambda _init_ctrls: wxNewId(), range(7))

class newFlagDialog(wxDialog):

    FLAG_DIR_NAME = 'flags'
    
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):

        # dialog box initialisation
        wxDialog.__init__(self, id=wxID_NEWFLAGDIALOG,
              name='newFlagDialog', parent=prnt, pos=wxPoint(0, 0),
              size=wxSize(300, 260), style=wxDEFAULT_DIALOG_STYLE,
              title='Flag')
        self._init_utils()
        self.SetClientSize(wxSize(300, 260))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the Solipsis icon in the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.nameStaticText = wxStaticText(id=wxID_NEWFLAGDIALOGNAMESTATICTEXT,
              label='Name :', name='nameStaticText', parent=self,
              pos=wxPoint(10, 20), size=wxSize(74, 15), style=0)

        self.nameTextCtrl = wxTextCtrl(id=wxID_NEWFLAGDIALOGNAMETEXTCTRL,
              name='nameTextCtrl', parent=self, pos=wxPoint(10, 40),
              size=wxSize(150, 20), style=0, value='')

        self.xposStaticText = wxStaticText(id=wxID_NEWFLAGDIALOGXPOSSTATICTEXT,
              label='X coordinate :', name='xposStaticText', parent=self,
              pos=wxPoint(10, 80), size=wxSize(78, 15), style=0)

        self.xposTextCtrl = wxTextCtrl(id=wxID_NEWFLAGDIALOGXPOSTEXTCTRL,
              name='xposTextCtrl', parent=self, pos=wxPoint(10, 100),
              size=wxSize(280, 20), style=0, value='')

        self.yposStaticText = wxStaticText(id=wxID_NEWFLAGDIALOGYPOSSTATICTEXT,
              label='Y coordinate :', name='yposStaticText', parent=self,
              pos=wxPoint(10, 140), size=wxSize(78, 15), style=0)

        self.yposTextCtrl = wxTextCtrl(id=wxID_NEWFLAGDIALOGYPOSTEXTCTRL,
              name='ypostextCtrl', parent=self, pos=wxPoint(10, 160),
              size=wxSize(280, 20), style=0, value='')

        self.okButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_ok_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_OK,
              name='okBitmapButton', parent=self, pos=wxPoint(32, 204),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.cancelButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_cancel_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CANCEL,
              name='cancelBitmapButton', parent=self, pos=wxPoint(190, 204),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        EVT_BUTTON(self.okButton, wxID_OK, self.OnOkButton)
        #EVT_BUTTON(self.cancelButton, wxID_CANCEL, self.OnCancelButton)

    def __init__(self, parent, navigator, flag_name):

        # navigator
        self.navigator = navigator

        # flag name (empty if new flag)
        self.flag_name = flag_name

        # init ctrls
        self._init_ctrls(parent)

        # init the position value in the dialog box
        self.initPositionValues()

    def initPositionValues(self):
        """ init the position values with the position of the connected node """
        
        # flag modification
        if self.flag_name:
            # open the flag file
            flagFile = newFlagDialog.FLAG_DIR_NAME + os.sep + self.flag_name
            try:
                f = file(flagFile, 'r')
            except:
                displayError(self, "Can not open the file " + flagFile)
                return 0

            # read file and close
            line = f.read()
            f.close()
            try:
                name, posX, posY = line.split(';')
            except:
                displayError(self, 'The file %s has a bad format !' %self.flag_name)
                # close the dialog box
                self.Close(FALSE)
                return 0

            # set default parameters
            self.nameTextCtrl.SetValue(name)
            self.xposTextCtrl.SetValue(posX)
            self.yposTextCtrl.SetValue(posY)

         # new flag -> check if the navigator is connected to a node
        elif (self.navigator.getIsConnected() == 1):
            posX = self.navigator.getNodePosX()
            posY = self.navigator.getNodePosY()
            self.xposTextCtrl.SetValue(str(posX))
            self.yposTextCtrl.SetValue(str(posY))

    def OnOkButton(self, event):
        """ save the flag with the parameter filled by the user """

        # get the parameters filled by the user
        name = self.nameTextCtrl.GetValue()
        posX = self.xposTextCtrl.GetValue()
        posY = self.yposTextCtrl.GetValue()

        # errors control
        if name == "":
            displayError(self, "Your flag name is empty !")
        elif posX == "":
            displayError(self, "Your flag X coordinate is empty !")
            messageDialog.ShowModal()
        elif posY == "":
            displayError(self, "Your flag Y coordinate is empty !")
        else:
            try:
                x = long(posX)
            except:
                displayError(self, "Your flag X coordinate has a bad format. Please, enter an integer.")
                return 0
            try:
                y = long(posY)
            except:
                displayError(self, "Your flag Y coordinate has a bad format. Please, enter an integer.")
                return 0

            flagFile = newFlagDialog.FLAG_DIR_NAME + os.sep + name

            # control the doublon
            if os.path.isfile(flagFile):
                displayError(self, "This flag name already exists. Please, choose another name.")
                return 0

            # flag modification
            if self.flag_name:
                # rename the flag file
                flagFile_old = newFlagDialog.FLAG_DIR_NAME + os.sep + self.flag_name
                os.rename(flagFile_old, flagFile)

            # open the flag file
            try:
                f = file(flagFile, 'w')
            except:
                displayError(self, 'Can not open the file %s' %flagFile)
                return 0

            # save the parameters in the flag file
            line = name + ';' + posX + ';'+ posY
            f.write(line)
            f.close()

            # close the dialog box
            self.Close(FALSE)
