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
## -----                           entityDialog.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the dialog box used by the user for entities management.
##
## ******************************************************************************

import wx
from image import ImageManager
from newLocalNodeDialog import newLocalNodeDialog
from newDistantNodeDialog import newDistantNodeDialog
from guiMessage import displayError
import os

def create(parent):
    return entityDialog(parent)

[wxID_ENTITYDIALOG, wxID_ENTITYDIALOGREMOVEBUTTON, wxID_ENTITYDIALOGNEWLOCALBUTTON,
 wxID_ENTITYDIALOGNEWDISTANTBUTTON, wxID_ENTITYDIALOGNODESLISTBOX,
 wxID_ENTITYDIALOGCONNECTBUTTON, wxID_ENTITYDIALOGDISCONNECTBUTTON,
] = map(lambda _init_ctrls: wx.NewId(), range(7))

class entityDialog(wx.Dialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):

        # dialog box initialisation
        wx.Dialog.__init__(self, id=wxID_ENTITYDIALOG, name='entityDialog',
              parent=prnt, pos=wx.Point(0, 0), size=wx.Size(386, 409),
              style=wx.DEFAULT_DIALOG_STYLE, title='Manage entities')
        self._init_utils()
        self.SetClientSize(wx.Size(378, 260))
        self.Center(wx.BOTH)
        self.SetBackgroundColour(wx.Colour(164, 202, 235))
                
        # set the icon of the dialog box
        iconSolipsis = ImageManager.getIcon(ImageManager.IMG_SOLIPSIS_ICON)
        self.SetIcon(iconSolipsis)

        self.nodesListBox = wx.ListBox(choices=self.pseudoList,
                                       id=wxID_ENTITYDIALOGNODESLISTBOX,
                                       name='nodesList', parent=self,
                                       pos=wx.Point(10, 20),size=wx.Size(210, 200),
                                       style=wx.LB_ALWAYS_SB,
                                       validator=wx.DefaultValidator)

        btmp = ImageManager.getButton(ImageManager.BUT_CREATE)
        self.newLocalButton = wx.BitmapButton(bitmap=btmp,
                                              id=wxID_ENTITYDIALOGNEWLOCALBUTTON,
                                              name='newlocalButton', parent=self,
                                              pos=wx.Point(260, 20),
                                              size=wx.Size(-1, -1), style=0,
                                              validator=wx.DefaultValidator)

        btmp = ImageManager.getButton(ImageManager.BUT_REMOVE)
        self.removeButton = wx.BitmapButton(bitmap=btmp,
                                            id=wxID_ENTITYDIALOGREMOVEBUTTON,
                                            name='removeButton', parent=self,
                                            pos=wx.Point(260, 60),
                                            size=wx.Size(-1, -1), style=0,
                                            validator=wx.DefaultValidator)

        btmp = ImageManager.getButton(ImageManager.BUT_CONNECT)
        self.connectButton = wx.BitmapButton(bitmap=btmp,
                                             id=wxID_ENTITYDIALOGCONNECTBUTTON,
                                             name='connectButton', parent=self,
                                             pos=wx.Point(260, 100),
                                             size=wx.Size(-1, -1), style=0,
                                             validator=wx.DefaultValidator)


        btmp = ImageManager.getButton(ImageManager.BUT_CLOSE_ENTITY)
        self.closeButton = wx.BitmapButton(bitmap=btmp, id=wx.ID_CANCEL,
                                           name='closeButton', parent=self,
                                           pos=wx.Point(260, 140),
                                           size=wx.Size(-1, -1), style=0,
                                           validator=wx.DefaultValidator)

        self.Bind(wx.EVT_LISTBOX, self.OnSelectNode,
                  id=wxID_ENTITYDIALOGNODESLISTBOX)
        #EVT_LISTBOX(self.nodesListBox, wxID_ENTITYDIALOGNODESLISTBOX,
        #     self.OnSelectNode)

        self.Bind(wx.EVT_BUTTON, self.OnNewLocalNodeButton,
                  id=self.newLocalButton.GetId())
        #self.Bind(EVT_BUTTON, self.OnNewLocalNodeButton, wxID_ENTITYDIALOGNEWLOCALBUTTON)
        
        self.Bind(wx.EVT_BUTTON, self.OnConnectNodeButton,
                  id=self.connectButton.GetId())        
        #self.Bind(wx.EVT_BUTTON, self.OnConnectNodeButton,
        #          id=wxID_ENTITYDIALOGCONNECTBUTTON
        

        self.Bind(wx.EVT_BUTTON, self.OnRemoveNodeButton,
                  id= self.removeButton.GetId())
        #self.Bind(wx.EVT_BUTTON, self.OnRemoveNodeButton,
        #          id=wxID_ENTITYDIALOGREMOVEBUTTON)
        
    def __init__(self, parent, controller):

        self.parent = parent
        # navigator
        self.controller = controller

        # create the nodes file in order to save the nodes created
        self.nodesDir = "nodes"
        if self.nodesDir not in os.listdir("."):
            os.mkdir(self.nodesDir)
        self.nodesFile = str(self.nodesDir) + os.sep + "nodes.txt"

        # init the nodes list
        self.nodeList = []
        self.pseudoList = []
        self.initNodesList()

        self.nodeIndice = -1

        # init ctrls
        self._init_ctrls(parent)


    def initNodesList(self):
        """ init the nodes list with the values read in the nodes file """

        # open the nodes file
        try:
            f = file(self.nodesFile, 'r')
        except:
            return 0

        # read file and close
        list = f.readlines()

        for line in list:
            [pseudo, host, port, controlPort, notifPort,
             posX, posY] = line.split(';')
            list={'pseudo':pseudo, 'host':host, 'port':port,
                  'controlPort': controlPort, 'notifPort': notifPort,
                  'posX':posX, 'posY':posY}
            self.nodeList.append(list)
            entry = pseudo
            self.pseudoList.append(entry)

        # close the file
        f.close()
        
        return 1

    def OnSelectNode(self, event):
        """ store the node selected by the user"""

        self.nodeIndice = self.nodesListBox.GetSelection()

    def OnNewLocalNodeButton(self, event):
        """ create a new local node in the list """

        dlg = newLocalNodeDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            pseudo = dlg.pseudoTextCtrl.GetValue()
            if pseudo == "":
                displayError(self, "Can't create the node : your node pseudo is empty !")
            else:
                self.controller.createNode(pseudo)                

    def OnNodeCreationFailure(self, reason):
        """ The node wasn't created"""
        displayError(self, 'Error, node not created: ' + reason)

    def OnNodeCreationSuccess(self):
        """ Success : node created"""
        self.initNodesList()


    def OnNewDistantNodeButton(self, event):
        """ create a new distant node in the list """

    