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

import wx
import wx.lib.newevent
from solipsis.navigator.controller import XMLRPCController, DummyController
from solipsis.navigator.navigatorinfo import NavigatorInfo

from solipsis.navigator.basic.image import ImageManager
from solipsis.navigator.basic.wxSubscriber import WxSubscriber
from solipsis.navigator.basic.wxProcessor import WxProcessor
from solipsis.navigator.basic.display2d import Display2D

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
] = map(lambda _init_ctrls: wx.NewId(), range(26))

# create event classes and event binder functions
NewPeerEvent, EVT_NEW_PEER       = wx.lib.newevent.NewEvent()
UpdatePeerEvent, EVT_UPDATE_PEER = wx.lib.newevent.NewEvent()
NodeInfoEvent, EVT_NODE_INFO     = wx.lib.newevent.NewEvent()
           
class wxMainFrame(wx.Frame):
    def _init_coll_menuBar_Menus(self, parent):

        # Entity menu
        self.menuEntity = wx.Menu()
        self.menuEntity.Append(wxID_WXMAINFRAMEMENUENTITYCONNECT, "Connect...", "")
        self.menuEntity.Append(wxID_WXMAINFRAMEMENUENTITYDISCONNECT, "Disconnect", "")
        self.menuEntity.Append(wxID_WXMAINFRAMEMENUENTITYQUIT, "Quit", "")
        # Add menu to the menu bar
        parent.Append(self.menuEntity, "Entity")

        # Flags menu
        self.menuFlags = wx.Menu()
        self.menuFlags.Append(wxID_WXMAINFRAMEMENUFLAGSADD, "Add flag", "")
        self.menuFlags.Append(wxID_WXMAINFRAMEMENUFLAGSTELEPORTATION, "Teleportation", "")
        self.menuFlags.Append(wxID_WXMAINFRAMEMENUFLAGSMANAGE, "Manage flags", "")

        parent.Append(self.menuFlags, "Flags")

        # 2D View menu
        self.menu2DView = wx.Menu()
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
        self.menuChat = wx.Menu()
        parent.Append(self.menuChat, "Chat")

        # Transfers menu
        self.menuTransfers = wx.Menu()
        parent.Append(self.menuTransfers, "Transfers")

        # About menu
        self.menuAbout = wx.Menu()
        self.menuAbout.Append(wxID_WXMAINFRAMEMENUABOUTSOLIPSIS, "About Solipsis", "")
        parent.Append(self.menuAbout, "?")

        # set the menu bar (tells the system we're done)
        self.SetMenuBar(parent)

        # evenement management
        self.Bind(wx.EVT_MENU, self.OnNodesConnect,
                  id=wxID_WXMAINFRAMEMENUENTITYCONNECT)
        
        self.Bind(wx.EVT_MENU, self.OnNodesDisconnect,
                  id=wxID_WXMAINFRAMEMENUENTITYDISCONNECT)
        self.Bind(wx.EVT_MENU, self.OnFlagsAdd,
                  id=wxID_WXMAINFRAMEMENUFLAGSADD)
        self.Bind(wx.EVT_MENU, self.OnFlagsTeleportation,
                  id=wxID_WXMAINFRAMEMENUFLAGSTELEPORTATION)
        self.Bind(wx.EVT_MENU, self.OnFlagsManage,
                  id=wxID_WXMAINFRAMEMENUFLAGSMANAGE)
        self.Bind(wx.EVT_MENU, self.OnImagesManage,
                  id=wxID_WXMAINFRAMEMENU2DVIEWMANAGE)
        self.Bind(wx.EVT_MENU, self.OnDisplayPseudos,
                  id=wxID_WXMAINFRAMEMENU2DVIEWDISPLAYPSEUDOS)
        self.Bind(wx.EVT_MENU, self.OnDisplayAvatars,
                  id=wxID_WXMAINFRAMEMENU2DVIEWDISPLAYAVATARS)
        self.Bind(wx.EVT_MENU, self.OnAvatarSize,
                  id=wxID_WXMAINFRAMEMENU2DVIEWAVATARSIZE)
        self.Bind(wx.EVT_MENU, self.OnAboutSolipsis,
                  id=wxID_WXMAINFRAMEMENUABOUTSOLIPSIS)
        self.Bind(wx.EVT_MENU, self.OnClose,
                  id=wxID_WXMAINFRAMEMENUENTITYQUIT) 
        
    def _init_utils(self):
        # generated method, don't edit
        self.menuBar = wx.MenuBar()
        self._init_coll_menuBar_Menus(self.menuBar)

    def _init_ctrls(self):

        # frame initialization
        wx.Frame.__init__(self, id=wxID_WXMAINFRAME, name='wxMainFrame',
                         parent=None, pos=wx.Point(0, 0), size=wx.Size(1024, 768),
                         style=wx.DEFAULT_FRAME_STYLE & ~
                         (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX),
                         title='Solipsis')
        self._init_utils()
        self.SetClientSize(wx.Size(1016, 741))

        # set the Solipsis icon in the frame
        iconSolipsis = ImageManager.getSolipsisIconWxIcon()
        bitmap = ImageManager.getSolipsisIconWxBitmap()
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        # navigation window
        self.navig_window = wx.Window(id=wxID_WXMAINFRAMENAVIG_WINDOW,
              name='navig_window', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(1014, 46), style=0)

        top = ImageManager.getTopBannerWxBitmap()
        self.bannerBitmap = wx.StaticBitmap(bitmap=top,
                                           id=wxID_WXMAINFRAMETOPBANNERBITMAP,
                                           name='topBannerBitmap',
                                           parent=self.navig_window,
                                           pos=wx.Point(0, 0), size=wx.Size(1014, 46),
                                           style=0)
        
        # logo window
        self.logo_window = wx.Window(id=wxID_WXMAINFRAMELOGO_WINDOW,
              name='logo_window', parent=self, pos=wx.Point(719, 46),
              size=wx.Size(295, 76), style=0)

        logo = ImageManager.getSolipsisLogoWxBitmap()
        self.logoBitmap = wx.StaticBitmap(bitmap=logo,
                                         id=wxID_WXMAINFRAMELOGOBITMAP,
                                         name='logoBitmap', parent=self.logo_window,
                                         pos=wx.Point(0, 0), size=wx.Size(295, 76),
                                         style=0)

        # 2D view window
        self.two_d_window = wx.Window(id=wxID_WXMAINFRAMETWO_D_WINDOW,
              name='two_d_window', parent=self, pos=wx.Point(0, 46),
              size=wx.Size(719, 676), style=0)

        # application window
        self.appli_window = wx.Window(id=wxID_WXMAINFRAMEAPPLI_WINDOW,
                                     name='appli_window', parent=self,
                                     pos=wx.Point(719, 122), size=wx.Size(295, 600),
                                     style=0)


        self.transferButton = wx.BitmapButton(bitmap=
                                             ImageManager.getBlueTransferWxBitmap(),
                                             id=wxID_WXMAINFRAMETRANSFERBUTTON,
                                             name='transferButton',
                                             parent=self.navig_window,
                                             pos=wx.Point(812, 9),
                                             size=wx.Size(100, 31), style=0,
                                             validator=wx.DefaultValidator)

        self.chatButton = wx.BitmapButton(bitmap=ImageManager.getRedChatWxBitmap(),
                                         id=wxID_WXMAINFRAMECHATBUTTON,
                                         name='chatButton',
                                         parent=self.navig_window,
                                         pos=wx.Point(912, 9), size=wx.Size(100, 31),
                                         style=wx.BU_AUTODRAW,
                                         validator=wx.DefaultValidator)

        self.chattersListBox = wx.ListBox(choices=[],
                                         id=wxID_WXMAINFRAMECHATTERSLISTBOX,
                                         name='chattersList',
                                         parent=self.appli_window,
                                         pos=wx.Point(6, 30), size=wx.Size(279,135),
                                         style=wx.NO_BORDER|wx.LB_ALWAYS_SB,
                                         validator=wx.DefaultValidator)

        self.chatTextCtrl = wx.TextCtrl(id=wxID_WXMAINFRAMECHATTEXTCTRL,
                                       name='chatTextCtrl',parent=self.appli_window,
                                       pos=wx.Point(6, 201), size=wx.Size(279, 233),
                                       style=wx.NO_BORDER|wx.TE_MULTILINE|wx.TE_READONLY,
                                       value='')

        self.messageTextCtrl = wx.TextCtrl(id=wxID_WXMAINFRAMEMESSAGETEXTCTRL,
                                          name='messageTextCtrl',
                                          parent=self.appli_window,
                                          pos=wx.Point(6, 460),size=wx.Size(279, 115),
                                          style=wx.NO_BORDER|wx.TE_MULTILINE,value='')

        sendBitmap =ImageManager.getBlueSendWxBitmap() 
        self.sendMessageButton = wx.BitmapButton(bitmap=sendBitmap,
                                                id=wxID_WXMAINFRAMESENDMESSAGEBUTTON,
                                                name='sendMessageButton',
                                                parent=self.appli_window,
                                                pos=wx.Point(190, 441),
                                                size=wx.Size(81, 17),
                                                validator=wx.DefaultValidator)

        

    def __init__(self, params):

        # init controls
        self._init_ctrls()
        
        # navigator information : node, peers, options, etc...
        self.navigatorInfo = NavigatorInfo(params)

        # 2D display functions are manged by the Display2D class
        self.display2d = Display2D(self.two_d_window, self.navigatorInfo)
        
        # navigator
        self.eventSubscriber = WxSubscriber(self)
        self.eventProcessor  = WxProcessor(self)
        #self.controller = XMLRPCController(self.eventSubscriber,
        #                                   params.getControlParams())
        self.controller = DummyController(self.eventSubscriber)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.two_d_window.Bind(wx.EVT_PAINT, self.display2d.OnPaint)
        
        # Bind events to the related processor function
        self.Bind(EVT_NEW_PEER, self.eventProcessor.OnNewPeer)
        self.Bind(EVT_UPDATE_PEER, self.eventProcessor.OnUpdatePeer)
        self.Bind(EVT_NODE_INFO, self.eventProcessor.OnNodeInfo)
        
    def OnNodesConnect(self, event):
        """ Open the entity manage dialog box on EntityManage event """
        self.controller.connect()
        #self.controller.lastNodeConnection()
        #self.entityDialog = entityDialog(self, self.controller)
        #self.entityDialog.ShowModal()

    def OnNodesDisconnect(self, event):
        """ Disconnect the controller from the current node on NodesDisconnect event """
        pass
        # display a confirmation message
        #message = 'Are you sure you want to disconnect you from the current entity ?'
        #dlg = wx.MessageDialog(self, message, 'Disconnect', wx.OK|wx.CANCEL|wx.CENTRE|wx.ICON_QUESTION)
        #dlg.Center(wx.BOTH)
        #if dlg.ShowModal() == wx.ID_OK:
        #    self.controller.disconnectNode(False)

    def OnImagesManage(self, event):
        #self.imagesDialog = imagesDialog(self, self.controller)
        #self.imagesDialog.ShowModal()
        pass
    
    def OnDisplayPseudos(self, event):
        """ change the display pseudos option """
        pass
        # save the new parameter value in the conf file
        #self.isDisplayPseudos = self.menu2DView.IsChecked(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYPSEUDOS)
        #configuration.writeConfParameterValue("displayPseudos", self.isDisplayPseudos)

        # refresh the display
        #self.toRefresh = TRUE

    def OnDisplayAvatars(self, event):
        """ change the display avatars option """
        pass
        # save the new parameter value in the conf file
        #self.isDisplayAvatars = self.menu2DView.IsChecked(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYAVATARS)
        #configuration.writeConfParameterValue("displayAvatars", self.isDisplayAvatars)

        # active the displayPseudos mode if the displayAvatars mode is desactivate
        #if self.isDisplayAvatars == 0:
        #    self.isDisplayPseudos = 1
        #    configuration.writeConfParameterValue("displayPseudos", self.isDisplayPseudos)

        # refresh the display
        #self.toRefresh = TRUE

    def OnAvatarSize(self, event):
        """ Display the avatar size dialog box """
        pass
        #dlg = avatarSizeDialog(self)
        #dlg.ShowModal()

    def OnAboutSolipsis(self, event):
        """ Display the about Solipsis dialog box """
        pass
        #dlg = aboutDialog(self)
        #dlg.ShowModal()
     
    def OnFlagsAdd(self, event):
        pass
        #self.addFlagDialog = flagsDialog(self, self.controller)
        #self.addFlagDialog.ShowModal()

    def OnFlagsTeleportation(self, event):
        pass
        #self.teleportationDialog = teleportationDialog(self, self.controller)
        #self.teleportationDialog.ShowModal()

    def OnFlagsManage(self, event):
        pass
        #self.manageFlagsDialog = flagsDialog(self, self.controller)
        #self.manageFlagsDialog.ShowModal()


    def OnFlagsGoto(self, event):
        """ Go to the flag selected in the menu """
        pass

    def On2DPaint(self, event):
        dc = wx.ClientDC(self.two_d_window)
        if len(self.navigatorInfo._peers) == 0:
            dc.DrawText('no peer', wx.Point(0,0))
        else:
            nb = len(self.navigatorInfo._peers)
            msg = 'Number of peers: ' + str(nb)
            dc.DrawText(msg, wx.Point(0,nb*20))
            
    def OnClose(self, event):
        """ Close the frame """

        # display a confirmation message
        message = 'Are you sure you want to quit the navigator ?'
        dlg = wx.MessageDialog(self, message, 'Quit', wx.OK|wx.CANCEL|wx.CENTRE|wx.ICON_QUESTION)
        dlg.Center(wx.BOTH)
        if dlg.ShowModal() == wx.ID_OK:
            self.Destroy()
