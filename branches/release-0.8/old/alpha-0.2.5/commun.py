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
## -----                           commun.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the commun functions used by all the modules of the application.
##
## ******************************************************************************

from wxPython.wx import *
import os
import configuration
# PIL
#import PIL.Image
#import PIL.PngImagePlugin
# don't look for more plugins
#PIL.Image._initialized = 1
from PIL import Image

# debug
import debug

# commun constantes
AVATAR_DIR_NAME = "Clash_Image"
if AVATAR_DIR_NAME not in os.listdir("."):
    os.mkdir(AVATAR_DIR_NAME)
RESIZE_DIR_NAME = "resize"
if RESIZE_DIR_NAME not in os.listdir(AVATAR_DIR_NAME):
    os.mkdir(AVATAR_DIR_NAME + os.sep + RESIZE_DIR_NAME)

FLAG_DIR_NAME = "Flags"
if FLAG_DIR_NAME not in os.listdir("."):
    os.mkdir(FLAG_DIR_NAME)    
    
def displayMessage(parent, message):
    """ Display an information message in the user interface """

    messageDialog = wxMessageDialog(parent, message, "Info", wxOK|wxCENTRE|wxICON_INFORMATION)
    messageDialog.Center(wxBOTH)
    messageDialog.ShowModal()

def displayError(parent, message):
    """ Display an error message in the user interface """

    messageDialog = wxMessageDialog(parent, message, "Error", wxOK|wxCENTRE|wxICON_ERROR)
    messageDialog.Center(wxBOTH)
    messageDialog.ShowModal()

def chgSize(avatarFile):
    """ change size of an image in accordance with size of avatars """
    debug.debug_info("commun.chgSize(" + avatarFile + ")")

    # open avatar file
    avatarImg = Image.open(avatarFile)
    # convert in RGBA format for transparency
    avatarImg = avatarImg.convert("RGBA")

    # resize the image file
    size = configuration.readConfParameterValue("avatarSize")
    if size:
        (width, height) = avatarImg.size
        newSize = width * int(size)/100
        if newSize < 5:
            # min size = 5 pixels
            newSize = 5
        avatarImg = avatarImg.resize((newSize, newSize))

    # save the resize image
    resizeFile = AVATAR_DIR_NAME + os.sep + RESIZE_DIR_NAME + os.sep + os.path.basename(avatarFile)
    avatarImg.save(resizeFile)
    return resizeFile
