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
## -----                           newDistantNodeDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for adding a new distant entity
##   to his list.
##
## ******************************************************************************

import wx

def create(parent):
    return newDistantNodeDialog(parent)

[wxID_NEWDISTANTNODEDIALOG,
 wxID_NEWDISTANTNODEDIALOGHOSTNODETEXT, wxID_NEWDISTANTNODEDIALOGHOSTTEXTCTRL,
 wxID_NEWDISTANTNODEDIALOGPORTNODETEXT, wxID_NEWDISTANTNODEDIALOGPORTTEXTCTRL,
] = map(lambda _init_ctrls: wx.NewId(), range(5))

class newDistantNodeDialog(wx.Dialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_NEWDISTANTNODEDIALOG,
              name='newDistantNodeDialog', parent=prnt, pos=wx.Point(0, 0),
              size=wx.Size(311, 203), style=wx.DEFAULT_DIALOG_STYLE,
              title='New node')
        self._init_utils()
        self.SetClientSize(wx.Size(230, 180))
        self.Center(wx.BOTH)
        self.SetBackgroundColour(wx.Colour(164, 202, 235))

        # set the icon of the dialog box
        iconSolipsis=wx.Icon('Img//icon_solipsis.png', wx.BITMAP_TYPE_PNG)
        bitmap=wx.Bitmap('Img//icon_solipsis.png',wx.BITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.hostNodeText = wx.StaticText(id=wxID_NEWDISTANTNODEDIALOGHOSTNODETEXT,
              label='Node host :', name='hostNodeText', parent=self,
              pos=wx.Point(10, 20), size=wx.Size(55, 13), style=0)

        self.portNodeText = wx.StaticText(id=wxID_NEWDISTANTNODEDIALOGPORTNODETEXT,
              label='Node port :', name='portNodeText', parent=self,
              pos=wx.Point(10, 80), size=wx.Size(53, 13), style=0)

        self.hostTextCtrl = wx.TextCtrl(id=wxID_NEWDISTANTNODEDIALOGHOSTTEXTCTRL,
              name='hostTextCtrl', parent=self, pos=wx.Point(70, 20),
              size=wx.Size(100, 21), style=0, value='')

        self.portTextCtrl = wx.TextCtrl(id=wxID_NEWDISTANTNODEDIALOGPORTTEXTCTRL,
              name='portTextCtrl', parent=self, pos=wx.Point(70, 80),
              size=wx.Size(100, 21), style=0, value='')

        self.okButton = wx.BitmapButton(bitmap=wx.Bitmap('Img//Buttons//bo_ok_n.png',
              wx.BITMAP_TYPE_PNG), id=wx.ID_OK,
              name='okButton', parent=self, pos=wx.Point(10, 130),
              size=wx.Size(78, 39), style=0,
              validator=wx.DefaultValidator)

        self.cancelButton = wx.BitmapButton(bitmap=wx.Bitmap('Img//Buttons//bo_cancel_n.png',
              wx.BITMAP_TYPE_PNG), id=wx.ID_CANCEL,
              name='cancelButton', parent=self, pos=wx.Point(140, 130),
              size=wx.Size(78, 39), style=0,
              validator=wx.DefaultValidator)

    def __init__(self, parent):
        self._init_ctrls(parent)
