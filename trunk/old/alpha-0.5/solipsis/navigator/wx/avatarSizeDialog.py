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
## -----                           avatarSizeDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for changing the size of
##   the avatars displayed in the 2D view.
##
## ******************************************************************************

from wxPython.wx import *
import configuration

import os

# PIL
import PIL.Image
import PIL.PngImagePlugin
# don't look for more plugins
PIL.Image._initialized = 1

import commun

# debug module
import debug

def create(parent):
    return avatarSizeDialog(parent)

[wxID_AVATARSIZEDIALOG, wxID_AVATARSIZEDIALOGMAXSTATICTEXT,
 wxID_AVATARSIZEDIALOGMINSTATICTEXT, wxID_AVATARSIZEDIALOGSIZESATICTEXT,
 wxID_AVATARSIZEDIALOGSIZESLIDER, wxID_AVATARSIZEDIALOGSIZETEXTCTRL,
] = map(lambda _init_ctrls: wxNewId(), range(6))

class avatarSizeDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_AVATARSIZEDIALOG,
              name='avatarSizeDialog', parent=prnt, pos=wxPoint(0, 0),
              size=wxSize(374, 299), style=wxDEFAULT_DIALOG_STYLE,
              title='Avatars size')
        self._init_utils()
        self.SetClientSize(wxSize(320, 240))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the icon of the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.sizeSaticText = wxStaticText(id=wxID_AVATARSIZEDIALOGSIZESATICTEXT,
              label='Define the size of the avatars displayed in the 2D view :',
              name='sizeSaticText', parent=self, pos=wxPoint(10, 20),
              size=wxSize(300, 15), style=0)

        self.sizeSlider = wxSlider(id=wxID_AVATARSIZEDIALOGSIZESLIDER,
              maxValue=100, minValue=0, name='sizeSlider', parent=self,
              point=wxPoint(40, 80), size=wxSize(200, 20),
              style=wxSL_HORIZONTAL, validator=wxDefaultValidator, value=0)

        self.minStaticText = wxStaticText(id=wxID_AVATARSIZEDIALOGMINSTATICTEXT,
              label='Min', name='minStaticText', parent=self, pos=wxPoint(10,
              80), size=wxSize(22, 15), style=0)

        self.maxStaticText = wxStaticText(id=wxID_AVATARSIZEDIALOGMAXSTATICTEXT,
              label='Max', name='maxStaticText', parent=self, pos=wxPoint(253,
              80), size=wxSize(26, 15), style=0)

        self.sizeTextCtrl = wxTextCtrl(id=wxID_AVATARSIZEDIALOGSIZETEXTCTRL,
              name='sizeTextCtrl', parent=self, pos=wxPoint(120, 110),
              size=wxSize(30, 21), style=0, value='')

        self.okButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_ok_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_OK,
              name='okButton', parent=self, pos=wxPoint(40, 180),
              size=wxSize(-1, -1), style=0, validator=wxDefaultValidator)

        self.cancelButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_cancel_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CANCEL,
              name='cancelButton', parent=self, pos=wxPoint(190, 180),
              size=wxSize(-1, -1), style=0, validator=wxDefaultValidator)

        EVT_SCROLL(self.sizeSlider, self.OnScrollSlider)
        EVT_BUTTON(self.okButton, wxID_OK, self.OnOkButton)

    def __init__(self, parent):
        self._init_ctrls(parent)

        # init the size slider
        self.initSizeSlider()

    def initSizeSlider(self):
        """ Initialize the size slider with the current size of avatars """

        # read the current size for the avatar in the conf file
        size = configuration.readConfParameterValue("avatarSize")
        if not size:
            # default size
            self.sizeSlider.SetValue(100)
            self.sizeTextCtrl.SetValue("100")
        else:
            self.sizeSlider.SetValue(int(size))
            self.sizeTextCtrl.SetValue(size)

    def OnScrollSlider(self,event):
        """ Intercept the scroll slider event to display the new size value """

        size = str(self.sizeSlider.GetValue())
        self.sizeTextCtrl.SetValue(size)

    def OnOkButton(self,event):
        """ Change the size of the avatars in the 2D view """
        debug.debug_info("avatarSizeDialog.OnOkButton()")
        size = self.sizeSlider.GetValue()

        # generate the avatars of the neighbors with the size value
        self.resizeAvatars(size)

        # save the new value in the conf file
        configuration.writeConfParameterValue("avatarSize", size)

        # close the dialog box
        self.Close(FALSE)

    def resizeAvatars(self, size):
        """ Resize the avatars of the neighbors """
        debug.debug_info("avatarSizeDialog.resizeAvatars(" + str(size) +")")
        # initialize the avatars list
        try:
            avatarsList = os.listdir(commun.AVATAR_DIR_NAME)
        except:
            # no avatar in the avatars directory
            return

        for avatar in avatarsList:
            avatarFile = commun.AVATAR_DIR_NAME + os.sep + avatar
            if os.path.isfile(avatarFile):
                # open avatar file
                debug.debug_info("avatarFile = " + avatarFile)
                avatarImg = PIL.Image.open(avatarFile)
                # convert in RGBA format for transparency
                avatarImg = avatarImg.convert("RGBA")

                # resize the image file
                (width, height) = avatarImg.size
                newSize = width * size/100
                if newSize < 5:
                    # min size = 5 pixels
                    newSize = 5
                avatarImg = avatarImg.resize((newSize, newSize))

                # save the resize image
                resizeFile = commun.AVATAR_DIR_NAME + os.sep + commun.RESIZE_DIR_NAME + os.sep + avatar
                avatarImg.save(resizeFile)
