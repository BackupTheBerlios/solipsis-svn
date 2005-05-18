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
## -----                           createAvatarDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for creating a new avatar.
##
## ******************************************************************************

from wxPython.wx import *
import os, tempfile
import commun

# PIL modules
import PIL.Image, PIL.ImageChops
import PIL.PngImagePlugin
import PIL.GifImagePlugin
import PIL.JpegImagePlugin
import PIL.BmpImagePlugin

# don't look for more plugins
PIL.Image._initialized = 1

# debug module
import debug

def create(parent):
    return createAvatarDialog(parent)

[wxID_CREATEAVATARDIALOG, wxID_CREATEAVATARDIALOGBROWSEBUTTON,
 wxID_CREATEAVATARDIALOGFILESTATICTEXT, wxID_CREATEAVATARDIALOGFILETEXTCTRL,
 wxID_CREATEAVATARDIALOGNAMESTATICTEXT, wxID_CREATEAVATARDIALOGNAMETEXTCTRL,
 wxID_CREATEAVATARDIALOGPREVIEWBUTTON, wxID_CREATEAVATARDIALOGAVATARBITMAP,
] = map(lambda _init_ctrls: wxNewId(), range(8))

class createAvatarDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_CREATEAVATARDIALOG,
              name='createAvatarDialog', parent=prnt, pos=wxPoint(22, 22),
              size=wxSize(768, 537), style=wxDEFAULT_DIALOG_STYLE,
              title='Create avatar')
        self._init_utils()
        self.SetClientSize(wxSize(365, 280))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the Solipsis icon in the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)
        
        # avatar bitmap
        self.avatarBitmap = ""
        
        self.nameStaticText = wxStaticText(id=wxID_CREATEAVATARDIALOGNAMESTATICTEXT,
              label='Avatar name :', name='nameStaticText', parent=self,
              pos=wxPoint(10, 20), size=wxSize(80, 15), style=0)

        self.nameTextCtrl = wxTextCtrl(id=wxID_CREATEAVATARDIALOGNAMETEXTCTRL,
              name='nameTextCtrl', parent=self, pos=wxPoint(10, 40),
              size=wxSize(100, 21), style=0, value='')

        self.fileStaticText = wxStaticText(id=wxID_CREATEAVATARDIALOGFILESTATICTEXT,
              label='Select your image file :', name='fileStaticText',
              parent=self, pos=wxPoint(10, 80), size=wxSize(140, 15), style=0)

        self.fileTextCtrl = wxTextCtrl(id=wxID_CREATEAVATARDIALOGFILETEXTCTRL,
              name='fileTextCtrl', parent=self, pos=wxPoint(10, 100),
              size=wxSize(260, 21), style=0, value='')

        self.browseButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_browse_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CREATEAVATARDIALOGBROWSEBUTTON,
              name='browseButton', parent=self, pos=wxPoint(280, 100),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.previewButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_preview_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CREATEAVATARDIALOGPREVIEWBUTTON,
              name='previewButton', parent=self, pos=wxPoint(10, 130),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.okButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_ok_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_OK,
              name='okButton', parent=self, pos=wxPoint(60, 220),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.cancelButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_cancel_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CANCEL,
              name='cancelButton', parent=self, pos=wxPoint(230, 220),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        EVT_BUTTON(self.browseButton, wxID_CREATEAVATARDIALOGBROWSEBUTTON,
                self.OnBrowseButton)

        EVT_BUTTON(self.previewButton, wxID_CREATEAVATARDIALOGPREVIEWBUTTON,
                self.OnPreviewButton)

        EVT_BUTTON(self.okButton, wxID_OK, self.OnOkButton)

    def __init__(self, parent):

        # directory for avatars
        self.avatarDir = 'Avatars'

        # image file name
        self.imageFileName = ""
        self.maskFileName = "Img" + os.sep + "mask.png"

        # avatar size
        self.avatarSize = 31

        # init controls in the dialog box
        self._init_ctrls(parent)

    def OnBrowseButton(self, event):
        """ Open a file dialog box to choose the image file """
        debug.debug_info("createAvatarDialog.OnBrowseButton()")

        wildcard = "Image files (*.bmp, *.jpg, *.gif, *.png)|*.bmp;*.jpg;*.gif;*.png"
        dlg = wxFileDialog(self, "Choose an image file", "", "", wildcard, wxOPEN)
        dlg.Center(wxBOTH)
        if dlg.ShowModal() == wxID_OK:
            # get the file name
            self.imageFileName=dlg.GetPath()
            self.fileTextCtrl.SetValue(self.imageFileName)
            debug.debug_info("imageFileName = " + self.imageFileName)

    def OnPreviewButton(self, event):
        """ Display the preview of the avatar """
        debug.debug_info("createAvatarDialog.OnPreviewButton()")

        # generate the result image
        resultImage=self.imageGeneration()
        if resultImage:
            # save the result image in a temporary file
            tmpDir = tempfile.gettempdir()
            debug.debug_info("tmpDir = " + tmpDir)
            if tmpDir:
                tmpFile = tmpDir + os.sep + "avatar.png"
                resultImage.save(tmpFile)
                # diplay the result image
                if not self.avatarBitmap:
                    self.avatarBitmap = wxStaticBitmap(bitmap=wxBitmap(tmpFile, wxBITMAP_TYPE_PNG),
                        id=wxID_CREATEAVATARDIALOGAVATARBITMAP,name='avatar',
                        parent=self, pos=wxPoint(110, 130),
                        size=wxSize(-1, -1), style=0)
                else:
                    self.avatarBitmap.SetBitmap(wxBitmap(tmpFile,wxBITMAP_TYPE_PNG))        
                # remove the temporary file
                os.remove(tmpFile)

    def OnOkButton(self, event):
        """ Save the avatar created by the user """

        # get the avatar name
        avatarName = self.nameTextCtrl.GetValue()
        if avatarName == "":
            commun.displayError(self, "Your avatar name is empty !")
        else:
            # generate the result image
            resultImage=self.imageGeneration()

            if resultImage:
                # save the result file with the name filled by the user
                avatarFile = self.avatarDir + os.sep + avatarName + ".png"
                # control the doublon
                if os.path.isfile(avatarFile):
                    commun.displayError(self, "This avatar name already exists. Please, choose another name.")
                    return 0

                resultImage.save(avatarFile)

                # close the dialog box
                self.Close(FALSE)

    def imageGeneration(self):
        """ Generate the result image """
        debug.debug_info("createAvatarDialog.imageGeneration()")

        # control errors
        if not self.imageFileName:
            commun.displayError(self, 'Please, select your image file !')
            return
        else:
            # open image files
            maskImg = PIL.Image.open(self.maskFileName)
            fileImg = PIL.Image.open(self.imageFileName)

            # contol the file size (for resizing)
            (width, height) = fileImg.size
            if ((width < self.avatarSize) or (height < self.avatarSize)):
                commun.displayError(self, 'Your image has a bad format. Please, choose a bigger one !')
                return

            # resize the image file with the size of avatars
            maskImg = maskImg.convert("RGBA")
            fileImg = fileImg.resize((self.avatarSize, self.avatarSize))
            fileImg = fileImg.convert("RGBA")
            resultImg = PIL.ImageChops.multiply(fileImg, maskImg)
            return resultImg
