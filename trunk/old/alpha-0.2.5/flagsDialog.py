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
## -----                           flagsDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for flags management.
##
## ******************************************************************************

from wxPython.wx import *
from newFlagDialog import *
import os

import commun

# debug module
import debug

def create(parent):
    return flagsDialog(parent)

[wxID_FLAGSDIALOG, wxID_FLAGSDIALOGCREATEBUTTON, wxID_FLAGSDIALOGREMOVEBUTTON,
 wxID_FLAGSDIALOGFLAGSLISTBOX, wxID_FLAGSDIALOGMODIFYBUTTON,
] = map(lambda _init_ctrls: wxNewId(), range(5))

class flagsDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_FLAGSDIALOG, name='flagsDialog',
              parent=prnt, pos=wxPoint(154, 154), size=wxSize(386, 298),
              style=wxDEFAULT_DIALOG_STYLE, title='Flags')
        self._init_utils()
        self.SetClientSize(wxSize(320, 240))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the Solipsis icon in the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.flagsListBox = wxListBox(choices=[],
              id=wxID_FLAGSDIALOGFLAGSLISTBOX, name='flagsListBox', parent=self,
              pos=wxPoint(10, 20), size=wxSize(160, 180), style=wxLB_ALWAYS_SB,
              validator=wxDefaultValidator)

        self.createButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_create_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_FLAGSDIALOGCREATEBUTTON,
              name='createButton', parent=self, pos=wxPoint(210, 20),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.modifyButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_modify_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_FLAGSDIALOGMODIFYBUTTON,
              name='modifyButton', parent=self, pos=wxPoint(210, 60),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.removeButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_remove_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_FLAGSDIALOGREMOVEBUTTON,
              name='removeButton', parent=self, pos=wxPoint(210, 100),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.closeButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_close_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CANCEL,
              name='closeButton', parent=self, pos=wxPoint(210, 140),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        EVT_LISTBOX(self.flagsListBox, wxID_FLAGSDIALOGFLAGSLISTBOX,
              self.OnSelectFlag)

        EVT_BUTTON(self.createButton, wxID_FLAGSDIALOGCREATEBUTTON,
              self.OnCreateButton)

        EVT_BUTTON(self.modifyButton, wxID_FLAGSDIALOGMODIFYBUTTON,
              self.OnModifyButton)

        EVT_BUTTON(self.removeButton, wxID_FLAGSDIALOGREMOVEBUTTON,
              self.OnRemoveButton)

    def __init__(self, parent, navigator):

        # init ctrls
        self._init_ctrls(parent)

        # navigator
        self.navigator = navigator

        # indice of the flag selected
        self.flagIndice = -1

        # init the flags list
        self.initFlagsList()

    def initFlagsList(self):
        """ init the flags list with the files in the Flags directory """
        debug.debug_info("flagsDialog.initFlagsList()")
        # clear the list
        self.flagsList = []
        self.flagsListBox.Clear()

        # initialize the flags list
        try:
            self.flagsList = os.listdir(commun.FLAG_DIR_NAME)
        except:
            pass

        # fill the list box
        for flag in self.flagsList:
            self.flagsListBox.Append(flag)

    def OnSelectFlag(self, event):
        """ store the flag indice selected by the user """

        # get flag indice in the list
        self.flagIndice = self.flagsListBox.GetSelection()

    def OnCreateButton(self, event):
        """ open the create flag dialog box """

        dlg = newFlagDialog(self, self.navigator, "")
        dlg.ShowModal()
        # refresh the flags list
        self.initFlagsList()

    def OnModifyButton(self, event):
        """ modify the flag selected """

        # check if an item is selected
        if (self.flagIndice != -1):

            # open the modify flag dialog box
            dlg = newFlagDialog(self, self.navigator, self.flagsList[self.flagIndice])
            dlg.ShowModal()

            # refresh the flags list
            self.initFlagsList()

    def OnRemoveButton(self, event):
        """ remove the flag selected """

        # check if an item is selected
        if (self.flagIndice != -1):
            # display a confirmation message
            flag = self.flagsList[self.flagIndice]
            message = 'Are you sure you want to remove this flag : ' + flag + ' ?'
            dlg = wxMessageDialog(self, message, 'Remove flag', wxOK|wxCANCEL|wxCENTRE|wxICON_QUESTION)
            dlg.Center(wxBOTH)
            if dlg.ShowModal() == wxID_OK:
                # remove the flag file
                flag_file = commun.FLAG_DIR_NAME + os.sep + flag
                os.remove(flag_file)

                # refresh the flags list
                self.initFlagsList()

            # destroy the dialog box
            dlg.Destroy()
