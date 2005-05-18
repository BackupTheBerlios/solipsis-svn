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
## -----                           chat.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the chat service.
##   It sends chat message to the neighbors and receive message from them.
##
## ******************************************************************************

import string
from service import *
from threading import Lock
import time
import wxMainFrame
from wxPython.wx import *
# debug module
import debug

class Chat(Service):

    def __init__(self, id_service, desc_service,  host, port, my_node, navigator):
        Service.__init__(self, id_service, desc_service,  host, port)

        # connected node
        self.my_node = my_node

        # navigator
        self.navigator = navigator

        self.mutex = Lock()

    def update(self, node, delta_x, delta_y):
        return 1


    def insert_service(self, node, host, port):
        #print "insert chat service (%s)" %node.id
        self.list_neighbors[node.id] = node
        #self.mutex.acquire()
        #self.navigator.displayChatterList()
        wxPostEvent(self.navigator.ihm, wxMainFrame.displayChatterListEvent())
        #self.mutex.release()
        
        return 1



    def delete_service(self, node):
        #print "chat.delete_service(%s)" %node.id
        if not self.list_neighbors.has_key(node.id):
            #print "ERROR, this neighbor %s is not in the list" %node.pseudo
            return 0

        else:

            del self.list_neighbors[node.id]
        text_to_display = "%s has left \n" %node.pseudo

        #self.mutex.acquire()
        # refresh the chatter list
        #self.navigator.deleteChatServiceNeighbor(node.id)        
        wxPostEvent(self.navigator.ihm, wxMainFrame.deleteChatServiceNeighborEvent(id=node.id))
        #self.navigator.displayChatterList()
        wxPostEvent(self.navigator.ihm, wxMainFrame.displayChatterListEvent())
        #self.mutex.release()

        return 1


    def broadcast(self, id, msg):
        """ Send a message """

        # get the message to send
        msgtosend = id + ";" + msg

        # send message to all neighbor in list_neighbor
        for chatter in self.list_neighbors.values():
            host, port = chatter.dict_service[self]
            self.udp_socket.sendto(msgtosend,(host, int(port)))

    def run(self):
        """ receive messages """

        self.alive = 1

        while self.alive:
            try:                
                # we put in place the time out
                time.sleep(0.1)
                self.udp_socket.setblocking(0)
                
                data, addr = self.udp_socket.recvfrom(1024)
                
                if not data : break

                else:

                    id_sender = string.splitfields(data, ";")[0]

                    if self.list_neighbors.has_key(id_sender):

                        # retrieve pseudo of sender
                        pseudo_sender = self.list_neighbors[id_sender].pseudo

                        # retrieve message
                        message = string.joinfields(string.splitfields(data, ";")[1:])

                        self.mutex.acquire()
                        #self.navigator.newChatMessage(pseudo_sender, message)
                        wxPostEvent(self.navigator.ihm, wxMainFrame.newChatMessageEvent(sender=pseudo_sender, message=message))
                        self.mutex.release()

                    #else:
                        #print "ERROR: this neighbor is not in the list_neighbor : %s" %id_sender
                        #return 0

            except:            
                pass

        debug.debug_info("End of Chat service ...")
