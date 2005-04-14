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
## -----                           wxMainFrame.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the main frame of SOLIPSIS navigator.
##   It initializes the navigator application and contains links
##   with all the graphic elements.
##
## ******************************************************************************

from wxPython.wx import *
from navigator import *
import configuration
import commun

# import for Dialog boxes
from entityDialog import *
from teleportationDialog import *
from addFlagDialog import *
from flagsDialog import *
from imagesDialog import *
from avatarSizeDialog import *
from aboutDialog import *

#from overBitmapButton import *
import sys, time, os

# debug module
import debug

from wxPython.lib import newevent

def create(parent):
    return wxMainFrame(parent)

[wxID_WXMAINFRAME, wxID_WXMAINFRAMEAPPLI_WINDOW,
 wxID_WXMAINFRAMEBANDEAUBITMAP, wxID_WXMAINFRAMECHATBITMAP,
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

# This creates a new Event class and a EVT binder function
displayChatterListEvent, EVT_DISPLAYCHATTERLIST = newevent.NewEvent()
deleteChatServiceNeighborEvent, EVT_DELETECHATSERVICENEIGHBOR = newevent.NewEvent()
newChatMessageEvent, EVT_NEWCHATMESSAGE = newevent.NewEvent()
addDisplay2dServiceNeighborEvent, EVT_ADDDISPLAY2DSERVICENEIGHBOR = newevent.NewEvent()
deleteDisplay2dServiceNeighborEvent, EVT_DELETEDISPLAY2DSERVICENEIGHBOR = newevent.NewEvent()
deleteImageEvent, EVT_DELETEIMAGE = newevent.NewEvent()
receiveImageEvent, EVT_RECEIVEIMAGE = newevent.NewEvent()
#newNeighborEvent, EVT_NEWNEIGHBOR = newevent.NewEvent()
#deleteNeighborEvent, EVT_DELETENEIGHBOR = newevent.NewEvent()
#updateNeighborEvent, EVT_UPDATENEIGHBOR = newevent.NewEvent()
#update2dViewEvent, EVT_UPDATE2DVIEW = newevent.NewEvent()
            
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

        # display the flags of the user in the flags menu
        """
        flagsList = []
        try:
            flagsList = os.listdir("Flags")
        except:
            pass
        if flagsList:
            self.menuFlags.InsertSeparator(3)
            for flag in flagsList:
                id = "wxID_WXMAINFRAMEMENUFLAGS" + flag
                id = wxNewId()
                self.menuFlags.Append(id, flag, "")
                EVT_MENU(self, id, self.OnFlagsGoto)
        """
        parent.Append(self.menuFlags, "Flags")

        # 2D View menu
        self.menu2DView = wxMenu()
        self.menu2DView.AppendCheckItem(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYPSEUDOS, "Display pseudos", "")
        self.menu2DView.AppendCheckItem(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYAVATARS, "Display avatars", "")                
        self.menu2DView.InsertSeparator(2)
        self.menu2DView.Append(wxID_WXMAINFRAMEMENU2DVIEWMANAGE, "Manage avatars", "")
        self.menu2DView.Append(wxID_WXMAINFRAMEMENU2DVIEWAVATARSIZE, "Avatars size", "")
        parent.Append(self.menu2DView, "2D View")

        # Chat menu
        self.menuChat = wxMenu()
        parent.Append(self.menuChat, "Chat")

        # Transfers menu
        self.menuTransfers = wxMenu()
        parent.Append(self.menuTransfers, "Transfers")

        # Options menu
        #self.menuOptions = wxMenu()
        #parent.Append(self.menuOptions, "Options")

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
        EVT_MENU_OPEN(self, self.OnOpenMenu)


    def _init_utils(self):
        # generated method, don't edit
        self.menuBar = wxMenuBar()
        self._init_coll_menuBar_Menus(self.menuBar)

    def _init_ctrls(self, prnt):

        # frame initialization
        wxFrame.__init__(self, id=wxID_WXMAINFRAME, name='wxMainFrame',
              parent=prnt, pos=wxPoint(0, 0), size=wxSize(1024, 768),
              style=wxDEFAULT_FRAME_STYLE & ~ (wxRESIZE_BORDER | wxRESIZE_BOX | wxMAXIMIZE_BOX),
              title='Solipsis')
        self._init_utils()
        self.SetClientSize(wxSize(1016, 741))
        #self.SetMenuBar(self.menuBar)

        # set the Solipsis icon in the frame
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        # navigation window
        self.navig_window = wxWindow(id=wxID_WXMAINFRAMENAVIG_WINDOW,
              name='navig_window', parent=self, pos=wxPoint(0, 0),
              size=wxSize(1014, 46), style=0)

        self.bandeauBitmap = wxStaticBitmap(bitmap=wxBitmap('Img//im_bandosup.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXMAINFRAMEBANDEAUBITMAP,
              name='bandeauBitmap', parent=self.navig_window, pos=wxPoint(0, 0),
              size=wxSize(1014, 46), style=0)
        
        # logo window
        self.logo_window = wxWindow(id=wxID_WXMAINFRAMELOGO_WINDOW,
              name='logo_window', parent=self, pos=wxPoint(719, 46),
              size=wxSize(295, 76), style=0)

        self.logoBitmap = wxStaticBitmap(bitmap=wxBitmap('Img//im_solipsis.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXMAINFRAMELOGOBITMAP,
              name='logoBitmap', parent=self.logo_window, pos=wxPoint(0, 0),
              size=wxSize(295, 76), style=0)

        # 2D view window
        self.two_d_window = wxWindow(id=wxID_WXMAINFRAMETWO_D_WINDOW,
              name='two_d_window', parent=self, pos=wxPoint(0, 46),
              size=wxSize(719, 676), style=0)

        # application window
        self.appli_window = wxWindow(id=wxID_WXMAINFRAMEAPPLI_WINDOW,
              name='appli_window', parent=self, pos=wxPoint(719, 122),
              size=wxSize(295, 600), style=0)

        #self.chatBitmap = wxStaticBitmap(bitmap=wxBitmap('Img//im_chat.png',
        #      wxBITMAP_TYPE_PNG), id=wxID_WXMAINFRAMECHATBITMAP,
        #      name='chatBitmap', parent=self.appli_window, pos=wxPoint(0, 0),
        #      size=wxSize(295, 600), style=0)

        self.transferButton = wxBitmapButton(bitmap=wxBitmap('Img//b_transf_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXMAINFRAMETRANSFERBUTTON,
              name='transferButton', parent=self.navig_window, pos=wxPoint(812,
              9), size=wxSize(100, 31), style=0,
              validator=wxDefaultValidator)

        self.chatButton = wxBitmapButton(bitmap=wxBitmap('Img//b_chat_a.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXMAINFRAMECHATBUTTON,
              name='chatButton', parent=self.navig_window, pos=wxPoint(912, 9),
              size=wxSize(100, 31), style=wxBU_AUTODRAW,
              validator=wxDefaultValidator)

        self.chattersListBox = wxListBox(choices=[], id=wxID_WXMAINFRAMECHATTERSLISTBOX,
              name='chattersList', parent=self.appli_window, pos=wxPoint(6, 30), size=wxSize(279,
              135), style=wxNO_BORDER|wxLB_ALWAYS_SB, validator=wxDefaultValidator)

        self.chatTextCtrl = wxTextCtrl(id=wxID_WXMAINFRAMECHATTEXTCTRL,
              name='chatTextCtrl', parent=self.appli_window, pos=wxPoint(6,
              201), size=wxSize(279, 233), style=wxNO_BORDER|wxTE_MULTILINE|wxTE_READONLY, value='')

        self.messageTextCtrl = wxTextCtrl(id=wxID_WXMAINFRAMEMESSAGETEXTCTRL,
              name='messageTextCtrl', parent=self.appli_window, pos=wxPoint(6,
              460), size=wxSize(279, 115), style=wxNO_BORDER|wxTE_MULTILINE, value='')

        self.sendMessageButton = wxBitmapButton(bitmap=wxBitmap('Img//send_n.png', wxBITMAP_TYPE_PNG), id=wxID_WXMAINFRAMESENDMESSAGEBUTTON,
              name='sendMessageButton', parent=self.appli_window,
              pos=wxPoint(190, 441), size=wxSize(81, 17),
              validator=wxDefaultValidator)

        EVT_PAINT(self.two_d_window, self.OnPaint2DView)
        EVT_PAINT(self.appli_window, self.OnPaintChatWindow)
        EVT_LEFT_DOWN(self.two_d_window, self.OnLeftDown)
        EVT_LEFT_DOWN(self.sendMessageButton, self.OnSendMessageButton)
        EVT_CHAR(self.messageTextCtrl, self.OnSendMessageButton)
        EVT_CLOSE(self, self.OnClose)
        
        # update IHM events
        EVT_DISPLAYCHATTERLIST(self, self.displayChatterList)
        EVT_DELETECHATSERVICENEIGHBOR(self, self.deleteChatServiceNeighbor)
        EVT_NEWCHATMESSAGE(self, self.newChatMessage)
        EVT_ADDDISPLAY2DSERVICENEIGHBOR(self, self.addDisplay2dServiceNeighbor)
        EVT_DELETEDISPLAY2DSERVICENEIGHBOR(self, self.deleteDisplay2dServiceNeighbor)
        EVT_DELETEIMAGE(self, self.deleteImage)
        EVT_RECEIVEIMAGE(self, self.receiveImage)
        #EVT_NEWNEIGHBOR(self, self.newNeighbor)
        #EVT_DELETENEIGHBOR(self, self.deleteNeighbor)
        #EVT_UPDATENEIGHBOR(self, self.updateNeighbor)
        #EVT_UPDATE2DVIEW(self, self.update2dView)
        
    def __init__(self, parent):

        # display variables
        self.dist_max = 2**127L        
        self.scale = 1.0
        self.coeff_zoom = 1

        # my node variables
        self.myNode_pseudo = ""
        self.myNode_ar = ""
        self.delta_x = 0
        self.delta_y = 0

        # displaying options
        self.isDisplayPseudos = 0
        val = configuration.readConfParameterValue("displayPseudos")
        if val:
            self.isDisplayPseudos = long(val)

        self.isDisplayAvatars = 1
        val = configuration.readConfParameterValue("displayAvatars")
        if val:
            self.isDisplayAvatars = long(val)

        # default images
        #self.myNode_avatar = 'Img//avat_gh.png'
        self.myNode_avatar = ""
        self.neighbor_avatar = 'Img//avat_gris.png'
        avatarFile = commun.AVATAR_DIR_NAME + os.sep + "neighbor_default.png"
        shutil.copyfile(self.neighbor_avatar, avatarFile)
        # resize the avatar file
        self.neighbor_avatar = commun.chgSize(avatarFile)

        # dictionary associating widget item with a neighbor
        # {[neighbor_id]:[neighbor_posX, neighbor_posY, neighbor_pseudo,
        #  neighbor_chat, neighbor_display2d, neighbor_sharing, neighbor_image]}
        self.neighbor_item = {}

        # init controls
        self._init_ctrls(parent)

        # navigator
        #self.navigator = Navigator(self, socket.gethostbyname(socket.gethostname()), "8080")
        self.navigator = Navigator(self)

        # refresh timer variables
        self.TIMER_ID = 1
        self.toRefresh = FALSE

        # start the timer to refresh displaying every second
        self.timer = wxTimer(self, self.TIMER_ID)
        EVT_TIMER(self, self.TIMER_ID, self.OnRefreshTimer)
        self.timer.Start(1000)
    
    def displayChatterList(self, event):
        self.navigator.displayChatterList()
    
    def deleteChatServiceNeighbor(self, event):
        """ delete the chat service picto of the corresponding neighbor """
        
        debug.debug_info("ihm.deleteChatServiceNeighbor()")        
        id=event.id
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][3] = FALSE
            # refresh the drawing
            self.toRefresh = TRUE
        debug.debug_info("ihm.deleteChatServiceNeighbor() OK")
        
    def newChatMessage(self, event):
        sender=event.sender
        message=event.message
        self.navigator.newChatMessage(sender, message)
    
    def addDisplay2dServiceNeighbor(self, event):
        debug.debug_info("ihm.addDisplay2dServiceNeighbor()")
        id=event.id
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][4] = TRUE
            # refresh the drawing
            self.toRefresh = TRUE
    
    def deleteDisplay2dServiceNeighbor(self, event):
        id=event.id
        debug.debug_info("ihm.deleteDisplay2dServiceNeighbor()")
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][4] = FALSE
            # refresh the drawing
            self.toRefresh = TRUE
        debug.debug_info("ihm.deleteDisplay2dServiceNeighbor() OK")
    
    def deleteImage(self, event):
        debug.debug_info("ihm.deleteImage()")
        id=event.id
        self.navigator.deleteImage(id)
        
    def receiveImage(self, event):
        sender=event.sender
        image_name=event.image_name
        self.navigator.receiveImage(sender, image_name)
        
#    def newNeighbor(self, event):
#        neighbor=event.neighbor
#        
#        debug.debug_info("ihm.insertNeighbor()")
#
#        # store the new neighbor item with no service and no image
#        self.neighbor_item[neighbor.id] = [neighbor.posX, neighbor.posY, neighbor.pseudo, FALSE, FALSE, FALSE, ""]
#
#        # refresh the drawing
#        #self.DoDrawing()
#        self.toRefresh = TRUE
        
#    def deleteNeighbor(self, event):
#        id=event.neighbor.id        
#        
#        # delete the neighbor item from the dictionnary
#        del self.neighbor_item[id]
#
#        # refresh the drawing
#        #self.DoDrawing()
#        self.toRefresh = TRUE
        
#    def updateNeighbor(self, event):
#        """ move the neighbor in the 2D view """
        
#        debug.debug_info("ihm.updateNeighbor()")
#        id=event.neighbor.id
#        delta_x=event.delta_x
#        delta_y=event.delta_y        
#        
#        # change the neighbor position
#        if self.neighbor_item.has_key(id):
#            # update the new coordinates of the neighbor
#            posX = long(self.neighbor_item[id][0] + delta_x)
#            if posX < -2**127L:
#                posX = long(posX + 2**128L)
#            elif posX > 2**127L:
#                posX = long(posX - 2**128L)

#            posY = long(self.neighbor_item[id][1] + delta_y)
#            if posY < -2**127L:
#                posY = long(posY + 2**128L)
#            elif posY > 2**127L:
#                posY = long(posY - 2**128L)

#            self.neighbor_item[id][0] = posX
#            self.neighbor_item[id][1] = posY

#            # refresh the drawing
#            self.toRefresh = TRUE

#    def update2dView(self, event):
#        self.navigator.update2dView()
        
    def OnOpenMenu(self, event):
        """ Refresh some menu items on Open Menu event """

        # check the connect/disconnect mode
        if (self.navigator.getIsConnected() == 1):
            enableMenu = TRUE
        else:
            enableMenu = FALSE

        # refresh flags menu with the flags list
        flagsMenuList = self.menuFlags.GetMenuItems()
        for menu in flagsMenuList:
            self.menuFlags.Remove(menu.GetId())
        self.menuFlags.Append(wxID_WXMAINFRAMEMENUFLAGSADD, "Add flag", "")
        self.menuFlags.Append(wxID_WXMAINFRAMEMENUFLAGSTELEPORTATION, "Teleportation", "")
        self.menuFlags.Append(wxID_WXMAINFRAMEMENUFLAGSMANAGE, "Manage flags", "")

        flagsList = []
        try:
            flagsList = os.listdir("Flags")
        except:
            pass
        if flagsList:
            self.menuFlags.InsertSeparator(3)
            for flag in flagsList:
                id = wxNewId()
                self.menuFlags.Append(id, flag, "")
                self.menuFlags.Enable(id, enableMenu)
                EVT_MENU(self, id, self.OnFlagsGoto)

        # enable/disable menus
        self.menuEntity.Enable(wxID_WXMAINFRAMEMENUENTITYDISCONNECT, enableMenu)
        self.menuFlags.Enable(wxID_WXMAINFRAMEMENUFLAGSADD, enableMenu)
        self.menuFlags.Enable(wxID_WXMAINFRAMEMENUFLAGSTELEPORTATION, enableMenu)

        # check/uncheck menus
        val=configuration.readConfParameterValue("displayPseudos")
        if val:
            self.menu2DView.Check(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYPSEUDOS, long(val))
        val=configuration.readConfParameterValue("displayAvatars")
        if val:
            self.menu2DView.Check(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYAVATARS, long(val))
        
    def OnRefreshTimer(self, event):
        """ call by the timer to refresh the 2D View if some change appeared """
        self.navigator.displayChatterList()
        if self.toRefresh == TRUE:
            self.DoDrawing()
            self.toRefresh = FALSE

    def OnPaint2DView(self, event):
        dc = wxPaintDC(self.two_d_window)
        self.DoDrawing(dc)

    def OnPaintChatWindow(self, event):
        dc = wxPaintDC(self.appli_window)
        # draw background picture
        two_d_bitmap = wxImage('Img//im_chat.png', wxBITMAP_TYPE_PNG).ConvertToBitmap()
        dc.DrawBitmap(two_d_bitmap, 0, 0, TRUE)

    def OnNodesConnect(self, event):
        """ Open the entity manage dialog box on EntityManage event """

        #self.navigator.lastNodeConnection()
        self.entityDialog = entityDialog(self, self.navigator)
        self.entityDialog.ShowModal()

    def OnNodesDisconnect(self, event):
        """ Disconnect the navigator from the current node on NodesDisconnect event """

        # display a confirmation message
        message = 'Are you sure you want to disconnect you from the current entity ?'
        dlg = wxMessageDialog(self, message, 'Disconnect', wxOK|wxCANCEL|wxCENTRE|wxICON_QUESTION)
        dlg.Center(wxBOTH)
        if dlg.ShowModal() == wxID_OK:
            self.navigator.disconnectNode(False)

    def OnImagesManage(self, event):
        self.imagesDialog = imagesDialog(self, self.navigator)
        self.imagesDialog.ShowModal()

    def OnDisplayPseudos(self, event):
        """ change the display pseudos option """
        debug.debug_info("ihm.OnDisplayPseudos()")

        # save the new parameter value in the conf file
        self.isDisplayPseudos = self.menu2DView.IsChecked(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYPSEUDOS)
        configuration.writeConfParameterValue("displayPseudos", self.isDisplayPseudos)

        # refresh the display
        self.toRefresh = TRUE

    def OnDisplayAvatars(self, event):
        """ change the display avatars option """
        debug.debug_info("ihm.OnDisplayAvatars()")

        # save the new parameter value in the conf file
        self.isDisplayAvatars = self.menu2DView.IsChecked(wxID_WXMAINFRAMEMENU2DVIEWDISPLAYAVATARS)
        configuration.writeConfParameterValue("displayAvatars", self.isDisplayAvatars)

        # active the displayPseudos mode if the displayAvatars mode is desactivate
        if self.isDisplayAvatars == 0:
            self.isDisplayPseudos = 1
            configuration.writeConfParameterValue("displayPseudos", self.isDisplayPseudos)

        # refresh the display
        self.toRefresh = TRUE

    def OnAvatarSize(self, event):
        """ Display the avatar size dialog box """
        debug.debug_info("ihm.OnAvatarSize()")
        dlg = avatarSizeDialog(self)
        dlg.ShowModal()

        # refresh the display (to change the avatar size)
        self.toRefresh = TRUE

    def OnAboutSolipsis(self, event):
        """ Display the about Solipsis dialog box """
        debug.debug_info("ihm.OnAboutSolipsis()")
        dlg = aboutDialog(self)
        dlg.ShowModal()
     
    def OnFlagsAdd(self, event):
        self.addFlagDialog = addFlagDialog(self, self.navigator)
        self.addFlagDialog.ShowModal()

    def OnFlagsTeleportation(self, event):
        self.teleportationDialog = teleportationDialog(self, self.navigator)
        self.teleportationDialog.ShowModal()

    def OnFlagsManage(self, event):
        self.manageFlagsDialog = flagsDialog(self, self.navigator)
        self.manageFlagsDialog.ShowModal()

    def removeFlagMenu(self, flag):
        self.manageFlagsDialog = flagsDialog(self, self.navigator)
        self.manageFlagsDialog.ShowModal()

    def OnFlagsGoto(self, event):
        """ Go to the flag selected in the menu """
        id = event.GetId()
        flag = self.menuFlags.GetLabel(id)
        debug.debug_info("ihm.OnFlagsGoto(" + flag +")")

        # display a confirmation message
        message = 'Are you sure you want to go to this flag : ' + flag + ' ?'
        dlg = wxMessageDialog(self, message, 'Go to flag', wxOK|wxCANCEL|wxCENTRE|wxICON_QUESTION)
        dlg.Center(wxBOTH)
        if dlg.ShowModal() == wxID_OK:
            # open the flag file
            flagFile = "Flags" + os.sep + flag
            try:
                f = file(flagFile, 'r')
            except:
                commun.displayError(self, 'Can not open the file %s' %flagFile)
                return 0

            # read file and close
            line = f.read()
            f.close()
            try:
                name, posX, posY = line.split(';')
            except:
                commun.displayError(self, 'The file %s has a bad format !' %flagFile)
                return 0
            
            # get the node AR to generate noise near the selected point
            ar = self.navigator.getNodeAr()
            debug.debug_info("getNodeAr() -> " + str(ar))
            deltaNoise = long(random.random()*ar/10)            
            posX = long(posX) + deltaNoise
            posY = long(posY) + deltaNoise
                
            # jump to the flag position
            self.navigator.jumpMyNode(str(posX), str(posY))

    def ClearDrawing(self, dc=None):
        #print "ihm.ClearDrawing()"
        if dc is None:
            dc = wxClientDC(self.two_d_window)

        # draw background picture
        two_d_bitmap = wxImage('Img//im_2D.png', wxBITMAP_TYPE_PNG).ConvertToBitmap()
        dc.DrawBitmap(two_d_bitmap, 0, 0, TRUE)

    def DoDrawing(self, dc=None):
        #print "ihm.DoDrawing()"
        if dc is None:
            dc = wxClientDC(self.two_d_window)

        # opions for the device context
        dc.SetBackground( wxBrush("White",wxSOLID) )
        #dc.SetBackgroundMode(wxSOLID)
        dc.SetBackgroundMode(wxTRANSPARENT)
        dc.SetFont( wxFont(10, wxSWISS, wxNORMAL, wxBOLD, FALSE) )
        dc.SetPen( wxPen("White",1) )
        dc.SetTextForeground("White")
        dc.SetBrush( wxBrush("White",wxTRANSPARENT) )


        # draw background picture
        two_d_bitmap = wxImage('Img//im_2D.png', wxBITMAP_TYPE_PNG).ConvertToBitmap()
        dc.DrawBitmap(two_d_bitmap, 0, 0, TRUE)

        # display the image and the pseudo of my node
        if self.myNode_pseudo :
            avatar_bitmap = wxImage(self.myNode_avatar, wxBITMAP_TYPE_PNG).ConvertToBitmap()

            self.pos_avatar_x = long(((self.two_d_window.GetClientSize().GetWidth()-avatar_bitmap.GetWidth()) /2) + self.delta_x)
            self.pos_avatar_y = long(((self.two_d_window.GetClientSize().GetHeight()-avatar_bitmap.GetHeight()) /2) + self.delta_y)
            dc.DrawBitmap(avatar_bitmap, self.pos_avatar_x,self.pos_avatar_y, TRUE)

            # display pseudo of my node
            if self.isDisplayPseudos == 1:
                self.pos_pseudo_x = self.pos_avatar_x
                self.pos_pseudo_y = long(self.pos_avatar_y + avatar_bitmap.GetHeight())
                dc.DrawText(self.myNode_pseudo, self.pos_pseudo_x, self.pos_pseudo_y)

            # we display the awarness radius
            if self.myNode_ar :
                # Coordinates of the square enclosing the circle
                #arInDisplay2d = long(self.newCoordinates(long(self.myNode_ar)))
                #dc.DrawCircle(self.pos_avatar_x, self.pos_avatar_y, arInDisplay2d)
                dc.DrawCircle(  self.two_d_window.GetClientSize().GetWidth()/2,
                                self.two_d_window.GetClientSize().GetHeight()/2,
                                self.two_d_window.GetClientSize().GetWidth()/2)

            # display neighbor items
            for neighbor_object in self.neighbor_item.values():

                # recompute position in the screen
                posX = long(self.newCoordinates(neighbor_object[0])+(self.two_d_window.GetClientSize().GetWidth() /2))
                posY = long(self.newCoordinates(neighbor_object[1])+(self.two_d_window.GetClientSize().GetHeight() /2))
                pseudo = neighbor_object[2]
                #print "display Neighbor : [%s]" %pseudo

                # display neighbor image if it belongs to the screen
                if 0 < posY < self.two_d_window.GetClientSize().GetHeight() and 0 < posX < self.two_d_window.GetClientSize().GetWidth():
                    #print "display Neighbor image : [%s]" %pseudo
                    # resize the image in accordance with the ar
                    #self.display2d.chgSize(id)

                    # get the photo image object
                    if self.isDisplayAvatars == 1:
                        if (neighbor_object[6]):
                            avatar_bitmap = wxImage(neighbor_object[6], wxBITMAP_TYPE_PNG).ConvertToBitmap()
                        else:
                            # if the neighbor has no image, display the default image
                            avatar_bitmap = wxImage(self.neighbor_avatar, wxBITMAP_TYPE_PNG).ConvertToBitmap()
                    else:
                        avatar_bitmap = wxImage("Img//avat_blanc.png", wxBITMAP_TYPE_PNG).ConvertToBitmap()

                    # display the image of neighbor
                    pos_avatar_x = long(posX-(avatar_bitmap.GetWidth())/2)
                    pos_avatar_y = long(posY-(avatar_bitmap.GetHeight())/2)
                    dc.DrawBitmap(avatar_bitmap, pos_avatar_x, pos_avatar_y, TRUE)

                    # display pseudo of the neighbor
                    if self.isDisplayPseudos == 1:
                        pos_pseudo_x = pos_avatar_x
                        pos_pseudo_y = long(pos_avatar_y + avatar_bitmap.GetHeight())
                        dc.DrawText(pseudo, pos_pseudo_x, pos_pseudo_y)

                    # display services picto bitmap
                    chat_bitmap = wxImage('Img//picto_chat.png', wxBITMAP_TYPE_PNG).ConvertToBitmap()
                    pos_chat_x = long(pos_avatar_x + avatar_bitmap.GetWidth())
                    pos_chat_y = pos_avatar_y

                    avat_bitmap = wxImage('Img//picto_avat.png', wxBITMAP_TYPE_PNG).ConvertToBitmap()
                    pos_avat_x = long(pos_avatar_x + avatar_bitmap.GetWidth())
                    pos_avat_y = long(pos_chat_y + chat_bitmap.GetHeight())

                    file_bitmap = wxImage('Img//picto_fichier.png', wxBITMAP_TYPE_PNG).ConvertToBitmap()
                    pos_file_x = long(pos_avatar_x + avatar_bitmap.GetWidth())
                    pos_file_y = long(pos_avat_y + avat_bitmap.GetHeight())


                    # display the image of neighbor chat service
                    if neighbor_object[3]:
                        dc.DrawBitmap(chat_bitmap, pos_chat_x, pos_chat_y, TRUE)

                    # display the image of neighbor display2d service
                    if neighbor_object[4]:
                        dc.DrawBitmap(avat_bitmap, pos_avat_x, pos_avat_y, TRUE)

                    # display the image of neighbor chat service
                    if neighbor_object[5]:
                        dc.DrawBitmap(file_bitmap, pos_file_x, pos_file_y, TRUE)

    def OnLeftDown(self, event):
        """ click on the display2d to move """
        #print "ihm.OnLeftDown()"

        # check if the navigator is connected to a node
        if (self.navigator.getIsConnected() == 1):

            # calculate the new node coordinates
            delta_x = event.m_x - self.pos_avatar_x
            delta_y = event.m_y - self.pos_avatar_y
            offset_x =  long( delta_x /(self.coeff_zoom * self.scale))
            offset_y =  long( delta_y/(self.coeff_zoom * self.scale))

            # display the node moving
            self.moveMyNode(delta_x, delta_y)

            # Inform the navigator
            mvt = str(offset_x) + ',' + str(offset_y)
            self.navigator.moveMyNode("POS",mvt)

    def moveMyNode(self, delta_x, delta_y):
        #print "ihm.moveMyNode(%d,%d)" %(delta_x, delta_y)
        for i in [1, 2, 3, 4]:
            self.delta_x = long(delta_x*i/4)
            self.delta_y = long(delta_y*i/4)
            # refresh the drawing
            self.DoDrawing()
            time.sleep(0.5)

        self.delta_x = 0
        self.delta_y = 0
        # refresh the drawing
        #self.ClearDrawing()
        #time.sleep(2)

    def startNavigator(self):
        """ start the navigator """
        self.navigator.connectNode()

    def setScale(self, ar):
        """ scale between the real distances and size of the display2d """
        
        debug.debug_info("ihm.setScale(%s)" %ar)
        
        # update max distance of Solipsis world displayed        
        if ar != 0:
            self.dist_max = ar

            # update scale for the screen
            sizeScreen = self.two_d_window.GetClientSize().GetWidth()
            self.scale = float( (sizeScreen / (2.0*ar) ))
        else:
            # if ar = 0 scale reinitialisation
            self.scale = 1

    def drawMyNode(self, pseudo, ar):
        debug.debug_info("ihm.drawMyNode")
        self.myNode_pseudo = pseudo
        self.myNode_ar = ar

        # default avatar
        avatarFile = commun.AVATAR_DIR_NAME + os.sep + pseudo + "_default.png"
        shutil.copyfile("Img//avat_gh.png", avatarFile)
        # resize the avatar file
        self.myNode_avatar = commun.chgSize(avatarFile)

        # refresh the drawing
        self.toRefresh = TRUE

    def drawMyAvatar(self, image_name):
        """ draw the avatar selected in the 2D View """
        debug.debug_info("ihm.drawMyAvatar()")

        self.myNode_avatar = image_name

        # refresh the drawing
        self.toRefresh = TRUE

    def insertNeighbor(self, id, posX, posY, pseudo):

        debug.debug_info("ihm.insertNeighbor()")

        # store the new neighbor item with no service and no image
        self.neighbor_item[id] = [posX, posY, pseudo, FALSE, FALSE, FALSE, ""]

        # refresh the drawing
        #self.DoDrawing()
        self.toRefresh = TRUE

    def updateNeighbor(self, id, delta_x, delta_y):
        """ move the neighbor in the 2D view """
        
        # change the neighbor position
        if self.neighbor_item.has_key(id):
            # update the new coordinates of the neighbor
            posX = long(self.neighbor_item[id][0] + delta_x)
            if posX < -2**127L:
                posX = long(posX + 2**128L)
            elif posX > 2**127L:
                posX = long(posX - 2**128L)

            posY = long(self.neighbor_item[id][1] + delta_y)
            if posY < -2**127L:
                posY = long(posY + 2**128L)
            elif posY > 2**127L:
                posY = long(posY - 2**128L)

            self.neighbor_item[id][0] = posX
            self.neighbor_item[id][1] = posY

            # refresh the drawing
            self.toRefresh = TRUE

    def deleteNeighbor(self, id):
        debug.debug_info("ihm.deleteNeighbor(%s)" %id)
        # delete the neighbor item from the dictionnary
        del self.neighbor_item[id]

        # refresh the drawing
        #self.DoDrawing()
        self.toRefresh = TRUE
        # refresh the chatter list
        #self.navigator.displayChatterList()
        debug.debug_info("ihm.deleteNeighbor() OK")

    def addChatServiceNeighbor(self, id):
        """ add the chat service picto of the corresponding neighbor """
    
        debug.debug_info("ihm.addChatServiceNeighbor()")   
        if self.neighbor_item.has_key(id):     
            self.neighbor_item[id][3] = TRUE
            # refresh the drawing
            #self.toRefresh = TRUE

#    def addDisplay2dServiceNeighbor(self, id):
#        """ add the display2d service picto of the corresponding neighbor """
#    
#        debug.debug_info("ihm.addDisplay2dServiceNeighbor()")
#        self.neighbor_item[id][4] = TRUE
#        # refresh the drawing
#        self.toRefresh = TRUE

#    def deleteChatServiceNeighbor(self, id):
#        """ delete the chat service picto of the corresponding neighbor """
#    
#        debug.debug_info("ihm.deleteChatServiceNeighbor()")
#        self.neighbor_item[id][3] = FALSE
#        # refresh the drawing
#        self.toRefresh = TRUE

#    def deleteDisplay2dServiceNeighbor(self, id):
#        """ delete the display2d service picto of the corresponding neighbor """
#    
#        debug.debug_info("ihm.deleteDisplay2dServiceNeighbor()")
#        self.neighbor_item[id][4] = FALSE
#        # refresh the drawing
#        self.toRefresh = TRUE

    def addSharefileServiceNeighbor(self, id):
        """ add the share file service picto of the corresponding neighbor """
        
        self.neighbor_item[id][5] = TRUE
        # refresh the drawing
        self.toRefresh = TRUE

    def displayNeighborImage(self, id, image_name):
        """ display the image of the neighbor in the display2d """
        
        # store the neighbor image
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][6] = image_name

            # refresh the drawing
            #self.DoDrawing()
            self.toRefresh = TRUE

    def deleteNeighborImage(self, id):
        """ delete the image of the neighbor in the display2d """
        debug.debug_info("ihm.deleteNeighborImage()")
        # delete the neighbor image
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][6] = ""

            # refresh the drawing
            self.toRefresh = TRUE
        debug.debug_info("ihm.deleteNeighborImage() OK")
        
    def newCoordinates(self, pos):
        """ return coordinates of a node in the display2d in accordance with its coordinates in the virtual world"""

        result = long(pos) * self.scale * self.coeff_zoom
        return result

    def clear2dView(self):
        """ clear all items displayed in 2D View """

        # my node variables
        self.myNode_pseudo = ""
        self.myNode_ar = ""
        #self.myNode_avatar = 'Img//avat_gh.png'

        # dictionary associating widget item with a neighbor
        # {[neighbor_id]:[neighbor_posX, neighbor_posY, neighbor_pseudo, neighbor_display2d, neighbor_chat]}
        self.neighbor_item = {}

        # refresh the drawing
        #self.DoDrawing()
        self.toRefresh = TRUE

    def clearChatterList(self):
        """ clear the chatters list """
        
        debug.debug_info("ihm.clearChatterList()")
        self.chattersListBox.Clear()
        debug.debug_info("ihm.clearChatterList() -> OK")
    
    def insertChatter(self, pseudo):    
        """ insert a new chatter in the chatters list """
        
        debug.debug_info("ihm.insertChatter(%s)" %pseudo)
        self.chattersListBox.Append(pseudo)
        debug.debug_info("ihm.insertChatter() -> OK")
    
    def deleteNeighborInChatterList(self, pseudo):
        """ delete a neighbor in the chatters list """
        
        debug.debug_info("ihm.deleteNeighborInChatterList(%s)" %pseudo)
        pos=self.chattersListBox.FindString(pseudo)
        debug.debug_info("ihm.deleteNeighborInChatterList pos =[%d]" %pos)
        self.chattersListBox.Delete(pos)
        debug.debug_info("ihm.deleteNeighborInChatterList() -> OK")
        
    def addMessageInChatText(self, text_to_display):
        self.chatTextCtrl.AppendText(text_to_display)

    def OnSendMessageButton(self,event):
        """ Send a message """
        
        # check the event
        if ((event.GetId() == wxID_WXMAINFRAMESENDMESSAGEBUTTON) or (event.GetKeyCode() == WXK_RETURN)):
            # get the message in the entry
            msg = self.messageTextCtrl.GetValue()
            # send the message to the navigator
            self.navigator.sendMessage(msg)
        else:
            event.Skip()    

    def delete_entry(self):
        """ refresh entry after sending message"""

        self.messageTextCtrl.Clear()

    def OnClose(self, event):
        """ Close the frame """

        # display a confirmation message
        message = 'Are you sure you want to quit the navigator ?'
        dlg = wxMessageDialog(self, message, 'Quit', wxOK|wxCANCEL|wxCENTRE|wxICON_QUESTION)
        dlg.Center(wxBOTH)
        if dlg.ShowModal() == wxID_OK:
            self.navigator.disconnectNode(True)
            self.Destroy()
