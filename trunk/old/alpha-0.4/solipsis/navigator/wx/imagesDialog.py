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
## -----                           imagesDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for images management.
##
## ******************************************************************************

from wxPython.wx import *
from createAvatarDialog import *
import os, shutil, string

import commun

def create(parent):
    return imagesDialog(parent)

[wxID_IMAGESDIALOG, wxID_IMAGESDIALOGCREATEBUTTON, wxID_IMAGESDIALOGREMOVEBUTTON,
 wxID_IMAGESDIALOGIMAGESLISTBOX, wxID_IMAGESDIALOGRENAMEBUTTON,
 wxID_IMAGESDIALOGCHOOSEBUTTON, wxID_IMAGESDIALOGAVATARBITMAP,
] = map(lambda _init_ctrls: wxNewId(), range(7))

class imagesDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):

        # avatar bitmap
        self.avatarBitmap = ""

        # dialog box initialisation
        wxDialog.__init__(self, id=wxID_IMAGESDIALOG, name='imagesDialog',
              parent=prnt, pos=wxPoint(0, 0), size=wxSize(386, 298),
              style=wxDEFAULT_DIALOG_STYLE, title='Manage avatars')
        self._init_utils()
        self.SetClientSize(wxSize(320, 260))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))

        # set the Solipsis icon in the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.imagesListBox = wxListBox(choices=[],
              id=wxID_IMAGESDIALOGIMAGESLISTBOX, name='imagesListBox',
              parent=self, pos=wxPoint(10, 20), size=wxSize(160, 180), style=wxLB_ALWAYS_SB,
              validator=wxDefaultValidator)

        self.chooseButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_choose_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_IMAGESDIALOGCHOOSEBUTTON,
              name='chooseButton', parent=self, pos=wxPoint(210, 20),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.createButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_create_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_IMAGESDIALOGCREATEBUTTON,
              name='createButton', parent=self, pos=wxPoint(210, 60),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.renameButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_rename_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_IMAGESDIALOGRENAMEBUTTON,
              name='renameButton', parent=self, pos=wxPoint(210, 100),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.removeButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_remove_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_IMAGESDIALOGREMOVEBUTTON,
              name='removeButton', parent=self, pos=wxPoint(210, 140),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.closeButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_close_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CANCEL,
              name='closeButton', parent=self, pos=wxPoint(210, 180),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        EVT_LISTBOX(self.imagesListBox, wxID_IMAGESDIALOGIMAGESLISTBOX,
              self.OnSelectImage)

        EVT_BUTTON(self.chooseButton, wxID_IMAGESDIALOGCHOOSEBUTTON,
              self.OnChooseButton)

        EVT_BUTTON(self.createButton, wxID_IMAGESDIALOGCREATEBUTTON,
              self.OnCreateButton)

        EVT_BUTTON(self.renameButton, wxID_IMAGESDIALOGRENAMEBUTTON,
              self.OnRenameButton)

        EVT_BUTTON(self.removeButton, wxID_IMAGESDIALOGREMOVEBUTTON,
              self.OnRemoveButton)

    def __init__(self, parent, navigator):

        # init ctrls
        self._init_ctrls(parent)

        # navigator
        self.navigator = navigator

        # directory for Avatars
        self.avatarsDir = 'Avatars'
        if self.avatarsDir not in os.listdir("."):
            self.avatarsDir = os.mkdir('Avatars')

        # indice of the image selected
        self.imageIndice = -1

        # init the images list
        self.imageList = []
        self.initImagesList()

    def initImagesList(self):
        """ init the images list with the files in the images directory """

        # clear the list
        self.imageList = []
        self.imagesListBox.Clear()

        try:
            self.imageList = os.listdir(self.avatarsDir)
        except:
            pass

        # fill the list box
        for i in range(len(self.imageList)):
            # delete the image extention
            (root, ext) = os.path.splitext(self.imageList[i])
            self.imageList[i] = root
            self.imagesListBox.Append(self.imageList[i])

    def OnSelectImage(self, event):
        """ store the image indice selected by the user """

        # get image indice in the list
        self.imageIndice = self.imagesListBox.GetSelection()

        # display the image selected
        image_name = self.avatarsDir + os.sep + self.imageList[self.imageIndice] + ".png"

        if not self.avatarBitmap:
            self.avatarBitmap = wxStaticBitmap(bitmap=wxBitmap(image_name,
                  wxBITMAP_TYPE_PNG), id=wxID_IMAGESDIALOGAVATARBITMAP,
                  name='avatar', parent=self, pos=wxPoint(80, 210),
                  size=wxSize(-1, -1), style=0)
        else:
            self.avatarBitmap.SetBitmap(wxBitmap(image_name,
                wxBITMAP_TYPE_PNG))

    def OnChooseButton(self, event):
        """ send the avatar selected to the neighbors """

        # check if an item is selected
        if (self.imageIndice != -1):
            # check if the navigator is connected to a node
            if (self.navigator.getIsConnected() == 1):
                # display a confirmation message
                message = 'Are you sure you want to send this avatar to your neighbors : ' + self.imageList[self.imageIndice] + ' ?'
                dlg = wxMessageDialog(self, message, 'Choose avatar', wxOK|wxCANCEL|wxCENTRE|wxICON_QUESTION)
                dlg.Center(wxBOTH)
                if dlg.ShowModal() == wxID_OK:
                    image_name = self.avatarsDir + os.sep + self.imageList[self.imageIndice] + ".png"
                    # copy the avatar in the avatarDir
                    avatarFile = commun.AVATAR_DIR_NAME + os.sep + self.navigator.getNodePseudo() + "_" + self.imageList[self.imageIndice] + ".png"
                    shutil.copyfile(image_name, avatarFile)
                    # resize the avatar file
                    resizeFile = commun.chgSize(avatarFile)
                    # send the file to the navigator                    
                    self.navigator.sendImage(avatarFile, resizeFile)
                    # close the dialog box
                    self.Close(FALSE)
            else:
                commun.displayError(self, 'Sorry you are not connected !')

    def OnCreateButton(self, event):
        """ create a new avatar image """

        # check if an item is selected
        dlg = createAvatarDialog(self)
        dlg.ShowModal()

        # refresh the avatars list
        self.initImagesList()

    def OnRenameButton(self, event):
        """ rename the image file selected """

        # check if an item is selected
        if (self.imageIndice != -1):
            dlg = wxTextEntryDialog(self, 'Rename your avatar :', 'Rename avatar', self.imageList[self.imageIndice], wxOK|wxCANCEL)
            dlg.Center(wxBOTH)
            if dlg.ShowModal() == wxID_OK:

                # get the new image name
                image_name = dlg.GetValue()
                if image_name == "":
                    commun.displayError(self, "Can't rename the avatar file : your name is empty !")
                else:
                    src = self.avatarsDir + os.sep + self.imageList[self.imageIndice] + ".png"
                    dest = self.avatarsDir + os.sep + image_name  + ".png"
                    # control the doublon
                    if os.path.isfile(dest):
                        commun.displayError(self, "This avatar name already exists. Please, choose another name.")
                    else:
                        # rename the image file
                        os.rename(src, dest)
                        # modify the image item in the list
                        self.imageList[self.imageIndice] = image_name
                        self.imagesListBox.SetString(self.imageIndice, image_name)

                # destroy the dialog box
                dlg.Destroy()


    def OnRemoveButton(self, event):
        """ remove the image selected """

        # check if an item is selected
        if (self.imageIndice != -1):
            # display a confirmation message
            message = 'Are you sure you want to remove this avatar : ' + self.imageList[self.imageIndice] + ' ?'
            dlg = wxMessageDialog(self, message, 'Remove avatar', wxOK|wxCANCEL|wxCENTRE|wxICON_QUESTION)
            dlg.Center(wxBOTH)
            if dlg.ShowModal() == wxID_OK:
                # remove the image file
                image_name = self.avatarsDir + os.sep + self.imageList[self.imageIndice] + ".png"
                os.remove(image_name)

                # remove the image item in the list
                del self.imageList[self.imageIndice]
                self.imagesListBox.Delete(self.imageIndice)

            # destroy the dialog box
            dlg.Destroy()
