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

        dlg = newDistantNodeDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            host = dlg.hostTextCtrl.GetValue()
            port = dlg.portTextCtrl.GetValue()
            if host == "":
                displayError(self, "Can't create the node : your node host is empty !")
            elif port == "":
                displayError(self, "Can't create the node : your node port is empty !")
            else:
                pseudo = host + ":" + port
                list={'pseudo':pseudo, 'host':host, 'port':port, 'posX':'', 'posY':'', 'isDistant':1, 'isConnected':0}

                # store the new node in the lists
                self.nodeList.append(list)
                self.pseudoList.append(pseudo)
                self.nodesListBox.Append(pseudo)

                # save the new node in the nodes file
                self.saveNodeFile()
        dlg.Destroy()

    def OnRemoveNodeButton(self, event):
        """ remove an entry in the nodes list """

        # check if an item is selected
        if (self.nodeIndice != -1):
            pseudo = self.nodeList[self.nodeIndice]['pseudo']
            host = self.nodeList[self.nodeIndice]['host']
            port = self.nodeList[self.nodeIndice]['port']
            isDistant = self.nodeList[self.nodeIndice]['isDistant']
            isConnected = self.nodeList[self.nodeIndice]['isConnected']
            connected_node = ""
            # display a confirmation message
            message = 'Are you sure you want to remove this entity : ' + pseudo + ' ?'
            dlg = wx.MessageDialog(self, message, 'Remove entity', wx.OK|wx.CANCEL|wx.CENTRE|wx.ICON_QUESTION)
            dlg.Center(wx.BOTH)
            if dlg.ShowModal() == wx.ID_OK:

                # kill the node if it's a local one
                if isDistant == 0:
                    #print "kill the node %s" %pseudo
                    if ((isConnected != 1) and (self.controller.getIsConnected() == 1)):
                        # the controller is connected to another node
                        connected_node = self.controller.my_node
                        self.controller.disconnectNode(False)

                    # connection with the node to kill
                    if self.controller.getIsConnected() == 0:
                        self.controller.connectNode(host, port)

                    # kill the node
                    self.controller.killNode()

                    # reconnect the controller to the current node
                    if connected_node != "":
                        self.controller.connectNode(connected_node.node_host, connected_node.node_port)

                # disconnect eventually from the distant node
                elif self.controller.getIsConnected() == 1:
                    self.controller.disconnectNode(False)

                # remove the node from the lists
                del self.nodeList[self.nodeIndice]
                del self.pseudoList[self.nodeIndice]
                self.nodesListBox.Delete(self.nodeIndice)

                # save the modification in the nodes file
                self.saveNodeFile()

            dlg.Destroy()
            self.nodeIndice = -1

    def saveNodeFile(self):
        """ save the nodes file with the value store in the nodes list """

        # open file 'nodes.txt'
        try:
            f = file(self.nodesFile, 'w')
        except:
            displayError(self, 'Cannot open the file %s' %self.nodesFile)
            return 0

        # write node infos in the nodes file
        for node in self.nodeList:
            pseudo = node['pseudo']
            host = node['host']
            port = str(node['port'])
            posX = str(node['posX'])
            posY = str(node['posY'])
            isDistant = str(node['isDistant'])
            isConnected = str(node['isConnected'])
            line = pseudo + ';' + host + ';'+ port + ';' + posX + ';' + posY + ';' + isDistant + ';' + isConnected + '\n'
            f.write(line)

        f.close()

        return 1

    def OnConnectNodeButton(self, event):
        """ connect the controller to the node selected in the list """

        # check if an item is selected and is not connected
        if ((self.nodeIndice != -1) and (self.nodeList[self.nodeIndice]['isConnected'] == 0)):
            pseudo = self.nodeList[self.nodeIndice]['pseudo']
            host = self.nodeList[self.nodeIndice]['host']
            port = self.nodeList[self.nodeIndice]['port']

            self.disconnectCurrentNode()
            return_val=self.controller.connectNode(host, port)            
            
            
            self.Close()

    def OnDisconnectNodeButton(self, event):
        """ disconnect the controller from the node selected in the list """

        # check if an item is selected and the corresponding node is connected
        if ((self.nodeIndice != -1) and (self.nodeList[self.nodeIndice]['isConnected'] == 1)):
            pseudo = self.nodeList[self.nodeIndice]['pseudo']

            # display a confirmation message
            message = 'Are you sure you want to disconnect you from this node : ' + pseudo + ' ?'
            dlg = wx.MessageDialog(self, message, 'Disconnect node', wx.OK|wx.CANCEL|wx.CENTRE|wx.ICON_QUESTION)
            dlg.Center(wx.BOTH)
            if dlg.ShowModal() == wx.ID_OK:

                # close the chat service
                #self.controller.closeChatService()

                # disconnect the controller from the node
                return_val=self.controller.disconnectNode(False)
                if return_val == 1:
                    # change the connected state of the node
                    self.nodeList[self.nodeIndice]['isConnected'] = 0
                    self.nodesListBox.SetString(self.nodeIndice, pseudo)

                    # save the disconnected node in the node file
                    self.saveNodeFile()

    def disconnectCurrentNode(self):
        """ disconnect from the current node """
        # find the current node in the list
        indice = 0
        for node in self.nodeList:
            if (node['isConnected'] == 1):
                # disconnect the controller from the node
                self.controller.disconnectNode(False)

                # change the connected state of the node
                self.nodeList[indice]['isConnected'] = 0
                self.nodesListBox.SetString(indice, self.nodeList[indice]['pseudo'])
                break

            indice +=1
