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
## -----                           navigator.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the interface module of the Solipsis navigator.
##   It is the interface between the application GUI and the communication
##   interfaces
##
## ******************************************************************************

from connection import *
from display2d import *
from chat import *
import commun

import string
import socket
import os
from sys import *
from threading import Lock

#from wxPython.wx import *
# debug module
import debug

#from wxPython.lib import newevent

#EVT_DISPLAYCHATTERLIST_ID = wxNewId()
#def EVT_DISPLAYCHATTERLIST(win, func):
#    win.Connect(-1, -1, EVT_DISPLAYCHATTERLIST_ID, func)

#class displayChatterListEvent(wxPyEvent):
#    """ Simple event to carry arbitrary result data """

#    def __init__(self):
#        wxPyEvent.__init__(self)        
#        self.SetEventType(EVT_DISPLAYCHATTERLIST_ID)


class Navigator:

    def __init__(self, ihm):        
        #self.mutex = Lock()
        self.ihm = ihm

        # boolean to know if the navigator is connected to a node or not
        self.isConnected = 0
        self.isChatActive = 0
        self.isDisplay2dActive = 0
        self.initNodesList()

        # update IHM events
        #EVT_DISPLAYCHATTERLIST(self.ihm, self.displayChatterList)
        
    def initNodesList(self):
        """ Nodes List initialisation : start the nodes dead in the list """

        #self.mutex.acquire()
        debug.debug_info("navigator.initNodesList()")

        # last connected node
        lastConnectedHost = ""
        lastConnectedPort = ""

        # open the nodes file
        self.nodesFile = str("Nodes") + os.sep + "Nodes.txt"
        try:
            f = file(self.nodesFile, 'r')
        except:
            #self.mutex.release()
            return 0

        # read file and close
        list = f.readlines()
        f.close()

        for line in list:
            pseudo, host, port, posX, posY, isDistant, isConnected = line[:len(line) -1].split(';')
            #print "read node file pseudo=[%s]" %pseudo
            #print "read node file port=[%s]" %port
            if (isConnected == "1"):
                # save the host and the port of the last node connected
                lastConnectedHost = host
                lastConnectedPort = port

            #try:
                # try to establish the connection with the node
                #my_node = MyNode(host, port, self)
                #my_node.launchConnection()
                #my_node.closeConnection()

            if not self.isNodeConnected(host, port):
                # start the node if the connection failed an the node is a local one
                if isDistant == "0":
                    self.startNode(pseudo, port, posX, posY)
                    commun.displayMessage(self.ihm, "The node " + pseudo + " was restarted !")
                else:
                    # print a message if a distant node is dead
                    commun.displayMessage(self.ihm, "The distant node " + pseudo + " is dead. You can delete it from your nodes list.")

        # connect the navigator to the last node connected
        # connect the navigator to the last node connected
        if ((lastConnectedHost != "") and (lastConnectedPort != "")):
            #self.connectNode(socket.gethostbyname(socket.gethostname()), lastConnectedPort)
            self.connectNode(lastConnectedHost, lastConnectedPort)

        #self.mutex.release()

    def startNode(self, pseudo, port, posX, posY):
        """ start a node with the given parameter """

        #self.mutex.acquire()
        debug.debug_info("navigator.startNode()")
        
        if platform == "win32":
            if ((posX != "") and (posY != "")):
                args = ['Node.exe', '-n', pseudo, '-t', str(port), '-x', str(posX), '-y', str(posY)]
            else:
                args = ['Node.exe', '-n', pseudo, '-t', str(port)]
            # spawn the node process
            os.spawnv(os.P_DETACH, args[0], args)
        else:            
            if ((posX != "") and (posY != "")):
                #args = [executable, 'Node.py', '-n', pseudo, '-t', str(port), '-x', str(posX), '-y', str(posY)]
                os.system(executable + " Node.py -n "+ pseudo+" -t "+str(port)+" > /dev/null &")

            else:
                #args = [executable, 'Node.py', '-n', pseudo, '-t', str(port)]
                os.system(executable + " Node.py -n "+ pseudo+" -t "+str(port)+" > /dev/null &")

        #self.mutex.release()

    def isNodeConnected(self, host, port):
        """ check if the node passed in parameter is alive """
        """ the function returns 1 if the node is alive and 0 if not """

        #self.mutex.acquire()
        debug.debug_info("navigator.isNodeConnected()")
        answer = 0

        # create TCP socket to send a isAlive signal to the node
        try:
            node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            node_socket.connect( (host, int(port)) )
        except:
            # the connection fails if the node is dead
            #self.mutex.release()
            return answer

        # send message
        msg = "isAlive"
        node_socket.send(msg)

        # waiting for answer
        answer = node_socket.recv(1024)
        node_socket.close()

        #self.mutex.release()
        return answer

    def connectNode(self, node_host, node_port):
        """ establish the connection with the node passed in parameter """

        debug.debug_info("navigator.connectNode()")
 
        try:
            # launch the node connection
            self.my_node = MyNode(node_host, node_port, self)
            self.my_node.launchConnection()

            # get information on the connected node
            self.my_node.getInfos()

            # add the services
            self.addChatService()
            self.addDisplay2dService()

            # change the connected status
            self.isConnected = 1

            # draw the 2d View after connection
            self.draw2dView()

            # refresh chatter
            #self.displayChatterList()
            return 1

        except:        
            commun.displayError(self.ihm, "Problem in the connection with the node !")
            return 0

    def disconnectNode(self, isQuit):
        """ close the connection with the node """

        debug.debug_info("navigator.disconnectNode(" + str(isQuit) + ")")
        if (self.isConnected == 1):
            #print "navigator.disconnectNode()"
            #f = file("Debug.txt", 'a')
            #f.write("navigator.disconnectNode()\n")
            #f.close()
            try:
                # save the last position of the node
                self.saveLastPositionNode(isQuit)

                # close the services
                self.closeChatService()
                self.closeDisplay2dService()

                # close the connection with the node
                self.my_node.closeConnection()
                self.isConnected = 0

                # clear ihm
                self.ihm.clear2dView()
                self.ihm.clearChatterList()               
                
                return 1

            except:
                #sys.stderr.write("EXCEPTION : Problem in the node deconnection\n")
                commun.displayError(self.ihm, "Problem in the disconnection from the node !")
                return 0

    def saveLastPositionNode(self, isQuit):
        """ Save the position of the last connected node """

        debug.debug_info("navigator.saveLastPositionNode(" + str(isQuit) + ")")
        if (self.isConnected == 1):

            # last connected node
            lastConnectedPseudo = self.getNodePseudo()
            lastConnectedPosX = self.getNodePosX()
            lastConnectedPosY = self.getNodePosY()
            #print "lastConnectedParameters:[%s,%d,%d]" %(lastConnectedPseudo, lastConnectedPosX, lastConnectedPosY)

            # open the nodes file
            self.nodesFile = str("Nodes") + os.sep + "Nodes.txt"
            try:
                f = file(self.nodesFile, 'r')
            except:                
                return 0

            # read and close file
            list = f.readlines()
            f.close()
            indice = 0

            for line in list:
                pseudo, host, port, posX, posY, isDistant, isConnected = line[:len(line) -1].split(';')
                if not isQuit:
                    isConnected = 0
                if pseudo == lastConnectedPseudo:
                    posX = lastConnectedPosX
                    posY = lastConnectedPosY

                    # write the new line in file
                    line = string.join((pseudo, host, str(port), str(posX), str(posY), str(isDistant), str(isConnected)), ';')
                    line += '\n'
                    list[indice] = line
                    break
                indice +=1

            # save the new lines in file
            try:
                f = file(self.nodesFile, 'w')
            except:
                return 0
            f.writelines(list)

            # close file
            f.close()

    def getIsConnected(self):
        """ return the connected status of the navigator """

        #self.mutex.acquire()
        debug.debug_info("navigator.getIsConnected()")
        connected_status = self.isConnected
        #self.mutex.release()
        return connected_status

    def getNodePosX(self):
        """ return the posX value of the connected node """

        #self.mutex.acquire()
        debug.debug_info("navigator.getNodePosX()")
        if (self.isConnected == 1):
            #self.mutex.release()
            return self.my_node.posX
        else:
            #self.mutex.release()
            return 0

    def getNodePosY(self):
        """ return the posY value of the connected node """

        #self.mutex.acquire()
        debug.debug_info("navigator.getNodePosY()")
        if (self.isConnected == 1):
            #self.mutex.release()
            return self.my_node.posY
        else:
            #self.mutex.release()
            return 0

    def getNodePseudo(self):
        """ return the pseudo value of the connected node """

        #self.mutex.acquire()
        debug.debug_info("navigator.getNodePseudo()")
        if (self.isConnected == 1):
            #self.mutex.release()
            return self.my_node.pseudo
        else:
            #self.mutex.release()
            return 0

    def getNodeAr(self):
        """ return the ar value of the connected node """

        #self.mutex.acquire()
        debug.debug_info("navigator.getNodeAr()")
        if (self.isConnected == 1):
            #self.mutex.release()
            return self.my_node.ar
        else:
            #self.mutex.release()
            return 0

    def addChatService(self):
        """ add the chat service to the navigator """

        debug.debug_info("navigator.addChatService()")

        # service object
        self.chat = Chat("Chat", 0, self.my_node.my_host, self.my_node.my_port_node+1, self.my_node, self)
        self.chat.start()

        # we fill the dictionary of my services
        self.my_node.services[self.chat.id_service] = self.chat

        # we inform the node we have the chat service
        self.my_node.addChatService()

        self.isChatActive = 1

    def closeChatService(self):
        """ Close the chat service """

        debug.debug_info("navigator.closeChatService()")

        if self.isChatActive == 1:
            # close the chat thread
            self.chat.close()

            # we delete the chat service from the dictionary of my services
            del self.my_node.services[self.chat.id_service]

            # we inform the node we have no longer the chat service
            self.my_node.closeChatService()

            self.isChatActive = 0

    def addDisplay2dService(self):
        """ add the display2d service to the navigator """

        debug.debug_info("navigator.addDisplay2dService()")
        # service object
        self.display2d = Display2d("Display2d", 0, self.my_node.my_host, self.my_node.my_port_node+2, self.my_node, self)
        self.display2d.start()

        # we fill the dictionary of my services
        self.my_node.services[self.display2d.id_service] = self.display2d

        # we inform the node we have the display2d service
        self.my_node.addDisplay2dService()

        self.isDisplay2dActive = 1

    def closeDisplay2dService(self):
        """ Close the display2d service """

        debug.debug_info("navigator.closeDisplay2dService()")

        if self.isDisplay2dActive == 1:
            # close the display2d thread
            self.display2d.close()
            # we delete the display 2D service from the dictionary of my services
            del self.my_node.services[self.display2d.id_service]

            # we inform the node we have no longer the display2d service
            self.my_node.closeDisplay2dService()
            self.isDisplay2dActive = 0

    def killNode(self):
        """ kill the current node """

        debug.debug_info("navigator.killNode()")

        if self.isConnected == 1:
            # send a kill message to the node
            self.my_node.kill()

            # close the services threads
            self.chat.close()
            self.display2d.close()

            # clear ihm
            self.ihm.clear2dView()
            self.ihm.clearChatterList()
            
            self.isConnected = 0

    def draw2dView(self):
        """ draw the 2D View of the node """

        #self.mutex.acquire()
        debug.debug_info("navigator.draw2dView()")

        # set scale of Solipsis world displayed
        self.ihm.setScale(self.my_node.ar)
        
        # draw my node
        self.ihm.drawMyNode(self.my_node.pseudo, self.my_node.ar)

        # refresh chatter
        #self.displayChatterList()
        #self.mutex.release()

    def update2dView(self):
        """ update the 2D View of the node """

        #self.mutex.acquire()
        debug.debug_info("navigator.update2dView()")

        # set scale of Solipsis world displayed
        self.ihm.setScale(self.my_node.ar)
        #self.mutex.release()

    def moveMyNode(self, var, delta):

        #self.mutex.acquire()
        debug.debug_info("navigator.moveMyNode()")
        self.my_node.modSelf(var, delta)
        #self.mutex.release()

    def jumpMyNode(self, x, y):

        #self.mutex.acquire()
        debug.debug_info("navigator.jumpMyNode()")

        if self.isConnected == 1:
            self.my_node.jump(x, y)
        #self.mutex.release()
    
    def displayChatterList(self):
        """ display the list of chatters available """

        #self.mutex.acquire()
        debug.debug_info("navigator.displayChatterList()")

        # check if the node is connected
        if self.isConnected == 1:
            self.ihm.clearChatterList()
            if self.chat.list_neighbors == {}:                
                self.ihm.insertChatter("No chatter")                
            else:

                for chatter in self.chat.list_neighbors.values():
                    self.ihm.insertChatter(chatter.pseudo)
                    self.ihm.addChatServiceNeighbor(chatter.id)                    

        #self.mutex.release()

    def newChatMessage(self, pseudo_sender, message):

        #self.mutex.acquire()
        debug.debug_info("navigator.newChatMessage()")

        # display message in window
        text_to_display = pseudo_sender + " says: " + message +"\n"
        self.ihm.addMessageInChatText(text_to_display)        
        #self.mutex.release()

    def deleteChatServiceNeighbor(self, id):
        """ delete the chat service of the node id """

        #self.mutex.acquire()
        debug.debug_info("navigator.deleteChatServiceNeighbor()")
        self.ihm.deleteChatServiceNeighbor(id)        
        #self.mutex.release()

    def deleteDisplay2dServiceNeighbor(self, id):
        """ delete the display2d service of the node id """

        #self.mutex.acquire()
        debug.debug_info("navigator.deleteDisplay2dServiceNeighbor()")

        self.ihm.deleteDisplay2dServiceNeighbor(id)        
        #self.mutex.release()

    def newNeighbor(self, neighbor):
        
        #self.mutex.acquire()
        debug.debug_info("navigator.newNeighbor()")
        self.ihm.insertNeighbor(neighbor.id, neighbor.posX, neighbor.posY, neighbor.pseudo)        
        #self.mutex.release()

    def deleteNeighbor(self, neighbor):
        
        #self.mutex.acquire()
        debug.debug_info("navigator.deleteNeighbor()")
        self.ihm.deleteNeighbor(neighbor.id)        
        # delete the neighbor in the chatter list
        #self.ihm.deleteNeighborInChatterList(neighbor.pseudo)
        #self.mutex.release()

    def updateNeighbor(self, neighbor, delta_x, delta_y):
        
        #self.mutex.acquire()
        debug.debug_info("navigator.updateNeighbor()")
        self.ihm.updateNeighbor(neighbor.id, delta_x, delta_y)        
        #self.mutex.release()

    def addDisplay2dServiceNeighbor(self, id):

        #self.mutex.acquire()
        debug.debug_info("navigator.addDisplay2dServiceNeighbor()")
        self.ihm.addDisplay2dServiceNeighbor(id)        
        #self.mutex.release()

    def addSharefileServiceNeighbor(self, id):

        #self.mutex.acquire()
        debug.debug_info("navigator.addSharefileServiceNeighbor()")
        self.ihm.addSharefileServiceNeighbor(id)
        #self.mutex.release()

    def sendMessage(self, msg):

        #self.mutex.acquire()
        debug.debug_info("navigator.sendMessage()")

        # check if the chat is active
        if (self.isChatActive == 1):

            # send a chat message
            self.chat.broadcast(self.my_node.id, msg)
            text_to_display ="I said: " +  msg + "\n"
            self.ihm.addMessageInChatText(text_to_display)            

            # delete the entry
            self.ihm.delete_entry()

        #self.mutex.release()

    def sendImage(self, avatarFile, resizeFile):

        #self.mutex.acquire()
        debug.debug_info("navigator.sendImage()")

        # check if the Display2d is active
        if (self.isDisplay2dActive == 1):

            # send my avatar to the neighbors
            self.display2d.sendImage(avatarFile)

            # display my avatar in the 2D View
            self.ihm.drawMyAvatar(resizeFile)

        #self.mutex.release()

    def receiveImage(self, sender, image_name):

        #self.mutex.acquire()
        debug.debug_info("navigator.receiveImage(" + sender + "," + image_name + ")")

        # check if the Display2d is active
        if (self.isDisplay2dActive == 1):
            self.ihm.displayNeighborImage(sender, image_name)            

        #self.mutex.release()

    def deleteImage(self, sender):

        #self.mutex.acquire()
        debug.debug_info("navigator.deleteImage()")

        # check if the Display2d is active
        if (self.isDisplay2dActive == 1):
            self.ihm.deleteNeighborImage(sender)            

        #self.mutex.release()
