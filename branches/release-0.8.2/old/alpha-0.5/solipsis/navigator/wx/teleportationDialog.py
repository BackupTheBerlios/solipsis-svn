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
## -----                           teleportationDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for teleportation in the
##   2D view.
##
## ******************************************************************************

from wxPython.wx import *
import random
import commun

# debug module
import debug

def create(parent):
    return teleportationDialog(parent)

[wxID_TELEPORTATIONDIALOG, wxID_TELEPORTATIONDIALOGCANCELBUTTON,
 wxID_TELEPORTATIONDIALOGOKBUTTON, wxID_TELEPORTATIONDIALOGXPOSSTATICTEXT,
 wxID_TELEPORTATIONDIALOGXPOSTEXTCTRL, wxID_TELEPORTATIONDIALOGYPOSSTATICTEXT,
 wxID_TELEPORTATIONDIALOGYPOSTEXTCTRL,
] = map(lambda _init_ctrls: wxNewId(), range(7))

class teleportationDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):

        # dialog box initialisation
        wxDialog.__init__(self, id=wxID_TELEPORTATIONDIALOG,
              name='teleportationDialog', parent=prnt, pos=wxPoint(0, 0),
              size=wxSize(320, 232), style=wxDEFAULT_DIALOG_STYLE,
              title='Teleportation')
        self._init_utils()
        self.SetClientSize(wxSize(300, 200))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the Solipsis icon in the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.xposStaticText = wxStaticText(id=wxID_TELEPORTATIONDIALOGXPOSSTATICTEXT,
              label='X coordinate :', name='xposStaticText', parent=self,
              pos=wxPoint(10, 20), size=wxSize(78, 12), style=0)

        self.yposStaticText = wxStaticText(id=wxID_TELEPORTATIONDIALOGYPOSSTATICTEXT,
              label='Y coordinate :', name='yposStaticText', parent=self,
              pos=wxPoint(10, 80), size=wxSize(78, 12), style=0)

        self.xposTextCtrl = wxTextCtrl(id=wxID_TELEPORTATIONDIALOGXPOSTEXTCTRL,
              name='xposTextCtrl', parent=self, pos=wxPoint(10, 40),
              size=wxSize(280, 20), style=0, value='')

        self.yposTextCtrl = wxTextCtrl(id=wxID_TELEPORTATIONDIALOGYPOSTEXTCTRL,
              name='ypostextCtrl', parent=self, pos=wxPoint(10, 100),
              size=wxSize(280, 20), style=0, value='')

        self.okButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_ok_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_TELEPORTATIONDIALOGOKBUTTON,
              name='okBitmapButton', parent=self, pos=wxPoint(32, 154),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)
        EVT_BUTTON(self.okButton, wxID_TELEPORTATIONDIALOGOKBUTTON,
              self.OnOkButton)

        self.cancelButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_cancel_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_TELEPORTATIONDIALOGCANCELBUTTON,
              name='cancelBitmapButton', parent=self, pos=wxPoint(190, 154),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)
        EVT_BUTTON(self.cancelButton, wxID_TELEPORTATIONDIALOGCANCELBUTTON,
              self.OnCancelButton)

    def __init__(self, parent, navigator):

        # navigator
        self.navigator = navigator

        # current position
        self.current_posx = 0
        self.current_posy = 0

        # init ctrls
        self._init_ctrls(parent)

        # init the position value in the dialog box
        self.initPositionValues()

    def initPositionValues(self):
        """ init the position values with the position of the connected node """

         # check if the navigator is connected to a node
        if (self.navigator.getIsConnected() == 1):
            self.current_posx = self.navigator.getNodePosX()
            self.current_posy = self.navigator.getNodePosY()
            self.xposTextCtrl.SetValue(str(self.current_posx))
            self.yposTextCtrl.SetValue(str(self.current_posy))

    def OnOkButton(self, event):
        """ teleportation of the connected node to the position filled """

        # check if the navigator is connected to a node
        if (self.navigator.getIsConnected() == 1):
            posx = self.xposTextCtrl.GetValue()
            posy = self.yposTextCtrl.GetValue()

            # errors control
            if posx == "":
                commun.displayError(self, "Your flag X coordinate is empty !")
            elif posy == "":
                commun.displayError(self, "Your flag Y coordinate is empty !")
            else:
                try:
                    x = long(posx)
                except:
                    commun.displayError(self, "Your flag X coordinate has a bad format. Please, enter an integer.")
                    return 0
                try:
                    y = long(posy)
                except:
                    commun.displayError(self, "Your flag Y coordinate has a bad format. Please, enter an integer.")
                    return 0

                # get the node AR to generate noise near the selected point
                ar = self.navigator.getNodeAr()
                #debug.debug_info("getNodeAr() -> " + str(ar))
                deltaNoise = long(random.random()*ar/10)
                #debug.debug_info("deltaNoise = [%d]" %deltaNoise)
                x = long(x + deltaNoise)
                y = long(y + deltaNoise)

                # Inform the navigator of the new position
                self.navigator.jumpMyNode(str(x), str(y))

                # close the dialog box
                self.Close(FALSE)
        else:
            commun.displayError(self, 'Sorry you are not connected !')

    def OnCancelButton(self, event):
        """ cancel action """

        # close the dialog box
        self.Close(FALSE)
