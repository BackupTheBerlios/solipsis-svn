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

from wxPython.wx import *
import random, time
import socket
import os
from sys import *
import commun
from newLocalNodeDialog import *
from newDistantNodeDialog import *

def create(parent):
    return entityDialog(parent)

[wxID_ENTITYDIALOG, wxID_ENTITYDIALOGREMOVEBUTTON, wxID_ENTITYDIALOGNEWLOCALBUTTON,
 wxID_ENTITYDIALOGNEWDISTANTBUTTON, wxID_ENTITYDIALOGNODESLISTBOX,
 wxID_ENTITYDIALOGCONNECTBUTTON, wxID_ENTITYDIALOGDISCONNECTBUTTON,
] = map(lambda _init_ctrls: wxNewId(), range(7))

class entityDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):

        # dialog box initialisation
        wxDialog.__init__(self, id=wxID_ENTITYDIALOG, name='entityDialog',
              parent=prnt, pos=wxPoint(0, 0), size=wxSize(386, 409),
              style=wxDEFAULT_DIALOG_STYLE, title='Manage entities')
        self._init_utils()
        self.SetClientSize(wxSize(378, 260))
        self.Center(wxBOTH)
        self.SetBackgroundColour(wxColour(164, 202, 235))
                
        # set the icon of the dialog box
        iconSolipsis=wxIcon('Img//icon_solipsis.png', wxBITMAP_TYPE_PNG)
        bitmap=wxBitmap('Img//icon_solipsis.png',wxBITMAP_TYPE_PNG)
        iconSolipsis.CopyFromBitmap(bitmap)
        self.SetIcon(iconSolipsis)

        self.nodesListBox = wxListBox(choices=self.pseudoList, id=wxID_ENTITYDIALOGNODESLISTBOX,
              name='nodesList', parent=self, pos=wxPoint(10, 20), size=wxSize(210,
              200), style=wxLB_ALWAYS_SB, validator=wxDefaultValidator)

        self.newLocalButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_createEntity_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_ENTITYDIALOGNEWLOCALBUTTON,
              name='newlocalButton', parent=self, pos=wxPoint(260, 20),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        #self.newDistantButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_newdistant_n.png',
        #      wxBITMAP_TYPE_PNG), id=wxID_ENTITYDIALOGNEWDISTANTBUTTON,
        #      name='newdistantButton', parent=self, pos=wxPoint(260, 60),
        #      size=wxSize(-1, -1), style=0,
        #      validator=wxDefaultValidator)

        self.removeButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_removeEntity_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_ENTITYDIALOGREMOVEBUTTON,
              name='removeButton', parent=self, pos=wxPoint(260, 60),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        self.connectButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_connect_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_ENTITYDIALOGCONNECTBUTTON,
              name='connectButton', parent=self, pos=wxPoint(260, 100),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)

        #self.disconnectButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_disconnect_n.png',
        #      wxBITMAP_TYPE_PNG), id=wxID_ENTITYDIALOGDISCONNECTBUTTON,
        #      name='disconnectButton', parent=self, pos=wxPoint(260, 140),
        #      size=wxSize(-1, -1), style=0,
        #      validator=wxDefaultValidator)

        self.closeButton = wxBitmapButton(bitmap=wxBitmap('Img//Buttons//bo_closeEntity_n.png',
              wxBITMAP_TYPE_PNG), id=wxID_CANCEL,
              name='closeButton', parent=self, pos=wxPoint(260, 140),
              size=wxSize(-1, -1), style=0,
              validator=wxDefaultValidator)
        #self.closeButton.Centre(wxHORIZONTAL)

        EVT_LISTBOX(self.nodesListBox, wxID_ENTITYDIALOGNODESLISTBOX,
              self.OnSelectNode)

        EVT_BUTTON(self.newLocalButton, wxID_ENTITYDIALOGNEWLOCALBUTTON,
              self.OnNewLocalNodeButton)

        #EVT_BUTTON(self.newDistantButton, wxID_ENTITYDIALOGNEWDISTANTBUTTON,
        #      self.OnNewDistantNodeButton)

        EVT_BUTTON(self.connectButton, wxID_ENTITYDIALOGCONNECTBUTTON,
              self.OnConnectNodeButton)

        #EVT_BUTTON(self.disconnectButton, wxID_ENTITYDIALOGDISCONNECTBUTTON,
        #      self.OnDisconnectNodeButton)

        EVT_BUTTON(self.removeButton, wxID_ENTITYDIALOGREMOVEBUTTON,
              self.OnRemoveNodeButton)
        
    def __init__(self, parent, navigator):

        # navigator
        self.navigator = navigator

        # create the nodes file in order to save the nodes created
        self.nodesDir = "Nodes"
        if self.nodesDir not in os.listdir("."):
            os.mkdir('Nodes')
        self.nodesFile = str(self.nodesDir) + os.sep + "Nodes.txt"

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
            pseudo, host, port, posX, posY, isDistant, isConnected = line[:len(line) -1].split(';')
            list={'pseudo':pseudo, 'host':host, 'port':port, 'posX':posX, 'posY':posY, 'isDistant':long(isDistant), 'isConnected':long(isConnected)}
            self.nodeList.append(list)
            entry = pseudo

            if ((list['isConnected'] == 1) and (self.navigator.getIsConnected() == 1)):
                entry +=' (connected)'
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
        if dlg.ShowModal() == wxID_OK:
            pseudo = dlg.pseudoTextCtrl.GetValue()
            if pseudo == "":
                commun.displayError(self, "Can't create the node : your node pseudo is empty !")
            else:
                #host = socket.gethostbyname(socket.gethostname())
                while 1:
                    # find a port available for the node
                    port = random.randint(1024, 2**16L)
                    try:
                        # start the new node
                        self.startNode(pseudo, port)
                        break
                    except:
                        # may be the port is already used
                        time.sleep(0.2)
                # host
                # DEB MOD MCL
                #addrinfo=socket.getaddrinfo(socket.gethostname(), port)
                #address=addrinfo[len(addrinfo)-1][4]
                #host=address[0]
                filename = str(pseudo)+".host"
                while filename not in os.listdir("."):
                    time.sleep(0.1)

                f = file(filename, 'r')
                host = f.readlines()[0]
                f.close()
                # FIN MOD MCL

                list={'pseudo':pseudo, 'host':host, 'port':port, 'posX':'', 'posY':'', 'isDistant':0, 'isConnected':0}

                # store the new node in the lists
                self.nodeList.append(list)
                self.pseudoList.append(pseudo)
                self.nodesListBox.Append(pseudo)

                # save the new node in the nodes file
                self.saveNodeFile()

        dlg.Destroy()

    def OnNewDistantNodeButton(self, event):
        """ create a new distant node in the list """

        dlg = newDistantNodeDialog(self)
        if dlg.ShowModal() == wxID_OK:
            host = dlg.hostTextCtrl.GetValue()
            port = dlg.portTextCtrl.GetValue()
            if host == "":
                commun.displayError(self, "Can't create the node : your node host is empty !")
            elif port == "":
                commun.displayError(self, "Can't create the node : your node port is empty !")
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
            dlg = wxMessageDialog(self, message, 'Remove entity', wxOK|wxCANCEL|wxCENTRE|wxICON_QUESTION)
            dlg.Center(wxBOTH)
            if dlg.ShowModal() == wxID_OK:

                # kill the node if it's a local one
                if isDistant == 0:
                    #print "kill the node %s" %pseudo
                    if ((isConnected != 1) and (self.navigator.getIsConnected() == 1)):
                        # the navigator is connected to another node
                        connected_node = self.navigator.my_node
                        self.navigator.disconnectNode(False)

                    # connection with the node to kill
                    if self.navigator.getIsConnected() == 0:
                        self.navigator.connectNode(host, port)

                    # kill the node
                    self.navigator.killNode()

                    # reconnect the navigator to the current node
                    if connected_node != "":
                        self.navigator.connectNode(connected_node.node_host, connected_node.node_port)

                # disconnect eventually from the distant node
                elif self.navigator.getIsConnected() == 1:
                    self.navigator.disconnectNode(False)

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
            commun.displayError(self, 'Can not open the file %s' %self.nodesFile)
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
        """ connect the navigator to the node selected in the list """

        # check if an item is selected and is not connected
        if ((self.nodeIndice != -1) and (self.nodeList[self.nodeIndice]['isConnected'] == 0)):
            f2 = file ("mytest1",'a')
            f2.write("if");
            f2.close()
            pseudo = self.nodeList[self.nodeIndice]['pseudo']
            host = self.nodeList[self.nodeIndice]['host']
            port = self.nodeList[self.nodeIndice]['port']

            # display a confirmation message
            #message = 'Are you sure you want to connect you to this node : ' + pseudo + ' ?'
            #dlg = wxMessageDialog(self, message, 'Connect node', wxOK|wxCANCEL|wxCENTRE|wxICON_QUESTION)
            #dlg.Center(wxBOTH)
            #if dlg.ShowModal() == wxID_OK:
            # disconnect from the current node before connecting to the new node
            self.disconnectCurrentNode()
            #self.navigator.connectNode(socket.gethostbyname(socket.gethostname()), port)
            return_val=self.navigator.connectNode(host, port)            
            
            if return_val == 1:
                # change the connected state of the node
                self.nodeList[self.nodeIndice]['isConnected'] = 1
                entry = pseudo + ' (connected)'
                self.nodesListBox.SetString(self.nodeIndice, entry)

                # save the new connected node in the node file
                self.saveNodeFile()

                # close the dialog box
                self.Close()

    def OnDisconnectNodeButton(self, event):
        """ disconnect the navigator from the node selected in the list """

        # check if an item is selected and the corresponding node is connected
        if ((self.nodeIndice != -1) and (self.nodeList[self.nodeIndice]['isConnected'] == 1)):
            pseudo = self.nodeList[self.nodeIndice]['pseudo']

            # display a confirmation message
            message = 'Are you sure you want to disconnect you from this node : ' + pseudo + ' ?'
            dlg = wxMessageDialog(self, message, 'Disconnect node', wxOK|wxCANCEL|wxCENTRE|wxICON_QUESTION)
            dlg.Center(wxBOTH)
            if dlg.ShowModal() == wxID_OK:

                # close the chat service
                #self.navigator.closeChatService()

                # disconnect the navigator from the node
                return_val=self.navigator.disconnectNode(False)
                if return_val == 1:
                    # change the connected state of the node
                    self.nodeList[self.nodeIndice]['isConnected'] = 0
                    self.nodesListBox.SetString(self.nodeIndice, pseudo)

                    # save the disconnected node in the node file
                    self.saveNodeFile()

    def startNode(self, pseudo, port):
        """ start a node with the given parameter """

        if platform == "win32":
            args = ['Node.exe', '-n', pseudo, '-t', str(port)]
            #os.spawnv(os.P_NOWAIT, args[0], args)
            os.spawnv(os.P_DETACH, args[0], args)
        else:
            #args = [executable, 'Node.py', '-n', pseudo, '-t', str(port)]
            os.system(executable + " Node.py -n "+ pseudo+" -t "+str(port)+" > /dev/null &")


    def disconnectCurrentNode(self):
        """ disconnect from the current node """


        # find the current node in the list
        indice = 0
        for node in self.nodeList:
            if (node['isConnected'] == 1):
                # disconnect the navigator from the node
                self.navigator.disconnectNode(False)

                # change the connected state of the node
                self.nodeList[indice]['isConnected'] = 0
                self.nodesListBox.SetString(indice, self.nodeList[indice]['pseudo'])
                break

            indice +=1
