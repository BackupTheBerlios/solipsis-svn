# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>
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

import wx
from image import ImageManager

def create(parent):
    return newLocalNodeDialog(parent)

[wxID_NEWLOCALNODEDIALOG, wxID_NEWLOCALNODEDIALOGCANCELBUTTON,
 wxID_NEWLOCALNODEDIALOGOKBUTTON, wxID_NEWLOCALNODEDIALOGPSEUDOSTATICTEXT,
 wxID_NEWLOCALNODEDIALOGPSEUDOTEXTCTRL,
] = map(lambda _init_ctrls: wx.NewId(), range(5))

class newLocalNodeDialog(wx.Dialog):
    """ Dialog for creating a new node on this machine"""
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_NEWLOCALNODEDIALOG,
              name='newLocalNodeDialog', parent=prnt, pos=wx.Point(0, 0),
              size=wx.Size(184, 173), style=wx.DEFAULT_DIALOG_STYLE,
              title='New node')
        self._init_utils()
        self.SetClientSize(wx.Size(230, 120))
        self.Center(wx.BOTH)
        self.SetBackgroundColour(wx.Colour(164, 202, 235))

        # set the icon of the dialog box
        iconSolipsis = ImageManager.getIcon(ImageManager.IMG_SOLIPSIS_ICON)
        bitmap = ImageManager.getBitmap(ImageManager.IMG_SOLIPSIS_ICON)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.pseudoStaticText = wx.StaticText(id=wxID_NEWLOCALNODEDIALOGPSEUDOSTATICTEXT,
              label='Node pseudo :', name='pseudoStaticText', parent=self,
              pos=wx.Point(10, 20), size=wx.Size(80, 15), style=0)
                
        self.pseudoTextCtrl = wx.TextCtrl(id=wxID_NEWLOCALNODEDIALOGPSEUDOTEXTCTRL,
              name='pseudoTextCtrl', parent=self, pos=wx.Point(100, 20),
              size=wx.Size(100, 21), style=0, value='')

        btmp = ImageManager.getButton(ImageManager.BUT_OK)
        self.okButton = wx.BitmapButton(bitmap=btmp, id=wx.ID_OK, name='okButton',
                                        parent=self, pos=wx.Point(10, 80),
                                        size=wx.Size(-1, -1), style=0,
                                        validator=wx.DefaultValidator)

        btmp = ImageManager.getButton(ImageManager.BUT_CANCEL)
        self.cancelButton = wx.BitmapButton(bitmap=btmp, id=wx.ID_CANCEL,
                                            name='cancelButton', parent=self,
                                            pos=wx.Point(140, 80),
                                            size=wx.Size(-1, -1), style=0,
                                            validator=wx.DefaultValidator)


    def __init__(self, parent):
        self._init_ctrls(parent)


