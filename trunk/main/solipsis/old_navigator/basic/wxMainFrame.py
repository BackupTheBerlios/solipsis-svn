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

## ---------------------------------------------------------------------------
## -----                           wxMainFrame.py                                  -----
## ---------------------------------------------------------------------------

## ****************************************************************************
##
##   This module is the main frame of SOLIPSIS navigator.
##   It initializes the navigator application and contains links
##   with all the graphic elements.
##
## ****************************************************************************

from wxPython.wx import *
from wxPython.lib import newevent

from solipsis.navigator.controller import Controller
from solipsis.navigator.nodeinfo import NodeInfo

from solipsis.navigator.basic.image import ImageManager

[wxID_WXMAINFRAME, wxID_WXMAINFRAMEAPPLI_WINDOW,
 wxID_WXMAINFRAMETOPBANNERBITMAP, wxID_WXMAINFRAMECHATBITMAP,
 wxID_WXMAINFRAMECHATBUTTON, wxID_WXMAINFRAMECHATTERSLISTBOX,
 wxID_WXMAINFRAMECHATTEXTCTRL, wxID_WXMAINFRAMELOGOBITMAP,
 wxID_WXMAINFRAMELOGO_WINDOW, wxID_WXMAINFRAMEMESSAGETEXTCTRL,
 wxID_WXMAINFRAMENAVIG_WINDOW, wxID_WXMAINFRAMESENDMESSAGEBUTTON,
 wxID_WXMAINFRAMETRANSFERBUTTON, wxID_WXMAINFRAMETWODVIEWBITMAP,
 wxID_WXMAINFRAMETWO_D_WINDOW, wxID_WXMAINFRAMEMENUENTITYCONNECT,
 wxID_WXMAINFRAMEMENUENTITYDISCONNECT, wxID_WXMAINFRAMEMENUENTITYQUIT,
 wxID_WXMAINFRAMEMENU2DVIEWMANAGE, wxID_WXMAINFRAMEMENUFLAGSADD,
 wxID_WXMAINFRAMEMENUFLAGSTELEPORTATION, wxID_WXMAINFRAMEMENUFLAGSMANAGE,
 wxID_WXMAINFRAMEMENU2DVIEWDISPLAYPSEUDOS, wxID_WXMAINFRAMEMENU2DVIEWDISPLAYAVATARS,
 wxID_WXMAINFRAMEMENU2DVIEWAVATARSIZE, wxID_WXMAINFRAMEMENUABOUTSOLIPSIS,
] = map(lambda _init_ctrls: wxNewId(), range(26))


class wxMainFrame(wxFrame):
    def _init_coll_menuBar_Menus(self, parent):

        # Entity menu
        self.menuEntity = wxMenu()
        self.menuEntity.Append(wxID_WXMAINFRAMEMENUENTITYCONNECT, "Connect...", "")
        self.menuEntity.Append(wxID_WXMAINFRAMEMENUENTITYDISCONNECT, "Disconnect", "")
        self.menuEntity.Append(wxID_WXMAINFRAMEMENUENTITYQUIT, "Quit", "")
        # Add menu to the menu bar
        parent.Append(self.menuEntity, "Entity")

        # Flags menu
        self.menuFlags = wxMenu()
        self.menuFlags.Append(wxID_WXMAINFRAMEMENUFLAGSADD, "Add flag", "")
        self.menuFlags.Append(wxID_WXMAINFRAMEMENUFLAGSTELEPORTATION, "Teleportation", "")
        self.menuFlags.Append(wxID_WXMAINFRAMEMENUFLAGSMANAGE, "Manage flags", "")

        parent.Append(self.menuFlags, "Flags")

        # 2D View menu
        self.menu2DView = wxMenu()
        self.menu2DView.AppendCheckItem(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYPSEUDOS,
                                        "Display pseudos", "")
        self.menu2DView.AppendCheckItem(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYAVATARS,
                                        "Display avatars", "")
        self.menu2DView.InsertSeparator(2)
        self.menu2DView.Append(wxID_WXMAINFRAMEMENU2DVIEWMANAGE,
                               "Manage avatars", "")
        self.menu2DView.Append(wxID_WXMAINFRAMEMENU2DVIEWAVATARSIZE,
                               "Avatars size", "")
        parent.Append(self.menu2DView, "2D View")

        # Chat menu
        self.menuChat = wxMenu()
        parent.Append(self.menuChat, "Chat")

        # Transfers menu
        self.menuTransfers = wxMenu()
        parent.Append(self.menuTransfers, "Transfers")

        # About menu
        self.menuAbout = wxMenu()
        self.menuAbout.Append(wxID_WXMAINFRAMEMENUABOUTSOLIPSIS, "About Solipsis", "")
        parent.Append(self.menuAbout, "?")

        # set the menu bar (tells the system we're done)
        self.SetMenuBar(parent)

        # evenement management
        EVT_MENU(self, wxID_WXMAINFRAMEMENUENTITYCONNECT, self.OnNodesConnect)
        EVT_MENU(self, wxID_WXMAINFRAMEMENUENTITYDISCONNECT, self.OnNodesDisconnect)
        EVT_MENU(self, wxID_WXMAINFRAMEMENUFLAGSADD, self.OnFlagsAdd)
        EVT_MENU(self, wxID_WXMAINFRAMEMENUFLAGSTELEPORTATION, self.OnFlagsTeleportation)
        EVT_MENU(self, wxID_WXMAINFRAMEMENUFLAGSMANAGE, self.OnFlagsManage)
        EVT_MENU(self, wxID_WXMAINFRAMEMENU2DVIEWMANAGE, self.OnImagesManage)
        EVT_MENU(self, wxID_WXMAINFRAMEMENU2DVIEWDISPLAYPSEUDOS, self.OnDisplayPseudos)
        EVT_MENU(self, wxID_WXMAINFRAMEMENU2DVIEWDISPLAYAVATARS, self.OnDisplayAvatars)
        EVT_MENU(self, wxID_WXMAINFRAMEMENU2DVIEWAVATARSIZE, self.OnAvatarSize)
        EVT_MENU(self, wxID_WXMAINFRAMEMENUABOUTSOLIPSIS, self.OnAboutSolipsis)
        EVT_MENU(self, wxID_WXMAINFRAMEMENUENTITYQUIT, self.OnClose)

    def _init_utils(self):
        # generated method, don't edit
        self.menuBar = wxMenuBar()
        self._init_coll_menuBar_Menus(self.menuBar)

    def _init_ctrls(self):

        # frame initialization
        wxFrame.__init__(self, id=wxID_WXMAINFRAME, name='wxMainFrame',
                         parent=None, pos=wxPoint(0, 0), size=wxSize(1024, 768),
                         style=wxDEFAULT_FRAME_STYLE & ~
                         (wxRESIZE_BORDER | wxRESIZE_BOX | wxMAXIMIZE_BOX),
                         title='Solipsis')
        self._init_utils()
        self.SetClientSize(wxSize(1016, 741))

        # set the Solipsis icon in the frame
        iconSolipsis = ImageManager.getSolipsisIconWxIcon()
        bitmap = ImageManager.getSolipsisIconWxBitmap()
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        # navigation window
        self.navig_window = wxWindow(id=wxID_WXMAINFRAMENAVIG_WINDOW,
              name='navig_window', parent=self, pos=wxPoint(0, 0),
              size=wxSize(1014, 46), style=0)

        top = ImageManager.getTopBannerWxBitmap()
        self.bannerBitmap = wxStaticBitmap(bitmap=top,
                                           id=wxID_WXMAINFRAMETOPBANNERBITMAP,
                                           name='topBannerBitmap',
                                           parent=self.navig_window,
                                           pos=wxPoint(0, 0), size=wxSize(1014, 46),
                                           style=0)

        # logo window
        self.logo_window = wxWindow(id=wxID_WXMAINFRAMELOGO_WINDOW,
              name='logo_window', parent=self, pos=wxPoint(719, 46),
              size=wxSize(295, 76), style=0)

        logo = ImageManager.getSolipsisLogoWxBitmap()
        self.logoBitmap = wxStaticBitmap(bitmap=logo,
                                         id=wxID_WXMAINFRAMELOGOBITMAP,
                                         name='logoBitmap', parent=self.logo_window,
                                         pos=wxPoint(0, 0), size=wxSize(295, 76),
                                         style=0)

        # 2D view window
        self.two_d_window = wxWindow(id=wxID_WXMAINFRAMETWO_D_WINDOW,
              name='two_d_window', parent=self, pos=wxPoint(0, 46),
              size=wxSize(719, 676), style=0)

        # application window
        self.appli_window = wxWindow(id=wxID_WXMAINFRAMEAPPLI_WINDOW,
                                     name='appli_window', parent=self,
                                     pos=wxPoint(719, 122), size=wxSize(295, 600),
                                     style=0)


        self.transferButton = wxBitm