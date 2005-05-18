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
## -----                           connection.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the connection interface with the node entity.
##   The XML-RPC interface with the node is implemented here.
##
## ******************************************************************************

import sys, xmlrpclib, string, math, time, socket, random, re
from math import ceil
from threading import Lock, Thread, Event
from SimpleXMLRPCServer import *
import StringIO
#import PIL.Image, ImageTk
import debug
import wxMainFrame
from wxPython.wx import *

# Size of the world
SIZE = [2**128L, 2**128L]

class Neighbor:
    """ all informations about a neighbor """

    def __init__(self, id, posX, posY, ca, pseudo, ori):

        # node  characteristics
        self.id = id
        self.posX = posX
        self.posY = posY
        self.ca = ca
        self.pseudo = pseudo
        self.ori = ori

        # node services
        # {[object_service]:[host,port]}
        self.dict_service = {}


    def movePos(self, delta_x, delta_y):
        """ this function changes the position of a neighbor in accordance with the moving """
        debug.debug_info("Neighbor.movePos()")
        # update the new coordinates of the neighbor
        self.posX = long(self.posX + delta_x)
        if self.posX < -2**127L:
            self.posX = long(self.posX + 2**128L)
        elif self.posX > 2**127L:
            self.posX = long(self.posX - 2**128L)

        self.posY = long(self.posY + delta_y)
        if self.posY < -2**127L:
            self.posY = long(self.posY + 2**128L)
        elif self.posY > 2**127L:
            self.posY = long(self.posY - 2**128L)

        return 1


    def deadNeighbor(self):
        """ this function removes the neighbor from the dictionary of services and the display2d """
        #print "Neighbor.deadNeighbor()"

        # we delete services of this neighbor
        for service in self.dict_service.keys():
            #service.delete_service(self)
            del service.list_neighbors[self.id]

        return 1


    def newService(self, object_service, host, port):
        """ the neighbor has a new service """

        # add service to self.dict_service
        self.dict_service[object_service] = [host,port]

        # signal presence to object_service
        object_service.insert_service(self, host, port)

        return 1


    def closeService(self, object_service):
        """ this method is called when a neighbor closes a service """

        if self.dict_service.has_key(object_service):

            # del service from dict_service (one or more services)
            del self.dict_service[object_service]

            # inform service
            object_service.delete_service(self)

        return 1


# ********************************************************************************
# --------------------------------------------------------------------------------
#               CALLABLE FUNCTIONS
# --------------------------------------------------------------------------------
# ********************************************************************************


class CallableFunction:
    """ Functions called by the node via its XML-RPC interface """

    def __init__(self, my_node):

        #self.mutex = Lock()

        # connected node
        self.my_node = my_node

    # closing of threads
    def close(self):

        self.my_node.closeConnection()

        return 1

    def Null():
        return 1


    def init(self, id, posX, posY, ar, ca, pseudo, ori):
        """ we call this function before all the others """
        debug.debug_info("connection.initNode(%s,%s)" %(posX, posY))
        self.my_node.id = id
        self.my_node.ori = int(ori)
        self.my_node.posX = string.atol(posX)
        self.my_node.posY = string.atol(posY)
        self.my_node.ar = string.atol(ar)
        self.my_node.ca = string.atol(ca)
        self.my_node.pseudo = pseudo

        # calculate the scale, fill the canvas and the listbox of chatters

        # DEB SUP MCL
        #self.mutex.acquire()
        #self.my_node.navigator.draw2dView()
        #self.my_node.navigator.displayChatterList()
        #self.mutex.release()
        # FIN SUP MCL


        return 1


    def newNode(self, id, posX, posY, ca, pseudo, ori):
        """ we meet a new node inside the awareness radius"""
        debug.debug_info("connection.newNode : [%s]" %pseudo)

        # we check this neighbor doesn't exist yet
        if not self.my_node.neighbors.has_key(id):

            #we create an object of the class 'Neighbor' as a representative of this node
            new_neighbor = Neighbor(id, long(posX), long(posY), long(ca), pseudo, int(ori))

            #insert in me's neighbors
            self.my_node.neighbors[id] = new_neighbor

        else:
            #print 'ERROR : node %s allready exists ' %pseudo
            return 0


        # we inform the navigator with this neighbor
        #self.mutex.acquire()
        self.my_node.navigator.newNeighbor(new_neighbor)
        #wxPostEvent(self.my_node.navigator.ihm, wxMainFrame.newNeighborEvent(neighbor=new_neighbor))
        #self.mutex.release()

        return 1

    def deadNode(self, id):
        """ a node gets out of the ar, we remove it from the neighbor list, service lists, interface 2d """
        debug.debug_info("CallableFunction.deadNode(%s)" %id)

        # we check the node exists
        if not self.my_node.neighbors.has_key(id) :
            #print "ERROR : The neighbor %s doesn't exist" %self.my_node.neighbors[id].pseudo
            return 0

        # remove the node from all dictionaries and from display2d, so we call 'deadNeighbor' method from 'Neighbor' class
        self.my_node.neighbors[id].deadNeighbor()
        #self.mutex.acquire()
        self.my_node.navigator.deleteNeighbor(self.my_node.neighbors[id])
        #wxPostEvent(self.my_node.navigator.ihm, wxMainFrame.deleteNeighborEvent(neighbor=self.my_node.neighbors[id]))
        #self.mutex.release()

        # remove from me's neighbors
        del self.my_node.neighbors[id]

        return 1



    def modNode(self, id, var, delta):
        """ modification of a node """
        debug.debug_info("CallableFunction.modNode(%s)" %id)
        #we check the node exists

        if not self.my_node.neighbors.has_key(id):
            #print "ERROR : The neighbor %s doesn't exist" %self.my_node.neighbors[id].pseudo
            return 0


        else:
            if var == 'POS':

                node = self.my_node.neighbors[id]

                # we update the coordinates so we call the method 'movePos' from 'Neighbor' object
                delta = string.split(delta,',')
                delta_x = long(delta[0])
                delta_y = long(delta[1])
                #self.mutex.acquire()
                node.movePos(delta_x,delta_y)
        
                # update the location of the node in the display2d
                self.my_node.navigator.updateNeighbor(node, delta_x, delta_y)
                #wxPostEvent(self.my_node.navigator.ihm, wxMainFrame.updateNeighborEvent(neighbor=node, delta_x=delta_x, delta_y=delta_y))
                #self.mutex.release()

                # update all services
                for service in node.dict_service.keys():
                    service.update(node, delta_x, delta_y)

            if var == 'CA':
                # we update self.ca
                self.my_node.neighbors[id].ca += string.atol(delta)


        return 1



    def modSelf(self, var, delta):
        """ modification of my node """
        #print "modification of my node with var =[%s]" %var
        debug.debug_info("modSelf(%s,%s)" %(var,delta))

        if var == 'POS':
            # we update our coordinates with 'updatePos' method from 'MyNode' class and update the coordinates
            # of the neighbors in accordance with our movement

            # modify my position
            delta = string.split(delta,',')
            delta_x = long(delta[0])
            delta_y = long(delta[1])

            #self.mutex.acquire()
            self.my_node.updatePos(delta_x, delta_y)
            #self.mutex.release()

        if var =='AR':

            # update ar and refresh the display
            long_delta = string.atol(delta)
            self.my_node.updateAr(long_delta)

            #self.mutex.acquire()
            # DEB MOD MCL
            #self.my_node.navigator.draw2dView()
            self.my_node.navigator.update2dView()
            #wxPostEvent(self.my_node.navigator.ihm, wxMainFrame.update2dViewEvent())
            # FIN MOD MCL
            #self.mutex.release()

        if var == 'CA':
            # 'updateCa' from 'MyNode' class

            int_delta = int(delta)
            self.my_node.updateCa(delta)


        if var == 'ORI':
            # 'updateOri' from 'MyNode' class

            self.my_node.updateOri(string.atol(delta))


        return 1



    def service(self, id_neighbor, id_service, desc_service, host, port):
        """ we are informed a neighbor has the service 'id_service' """
        #print "connection.service(%s, %s)" %(id_neighbor, id_service)

        # retrieve the service object (if exists) from self.services
        if not self.my_node.services.has_key(id_service):
            #print "My node has not this service %s" %id_service
            return 0
        else:

            object_service = self.my_node.services[id_service]


        # retrieve the neighbor object (if exists) from self.neighbors
        if not self.my_node.neighbors.has_key(id_neighbor) :
            #print "ERROR: this neighbor %s doesn't exist"  %self.my_node.services[id_neighbor].pseudo
            return 0

        else:
            # insert this service in the dictionary of services and signal it presence to service object
            #self.mutex.acquire()
            self.my_node.neighbors[id_neighbor].newService(object_service, host, port)
            #self.mutex.release()

        return 1


    def closeService(self, id_neighbor, id_service):
        """ we are informed a neighbor closes his service: id_service """
        #print "closeService(%s)" %id_neighbor
        if not self.my_node.services.has_key(id_service):
            #print "My node has not this service %s" %id_service
            return 0
        else:
            object_service = self.my_node.services[id_service]

        if not self.my_node.neighbors.has_key(id_neighbor):
            #print "This neighbor %s is not here" %self.my_node.neighbors[id_neighbor].pseudo
            return 0
        else:
            self.my_node.neighbors[id_neighbor].closeService(object_service)

        return 1


# ********************************************************************************
# --------------------------------------------------------------------------------
#               NODE COM
# --------------------------------------------------------------------------------
# ********************************************************************************

class NodeCom(Thread):
    """ class for communication with the node """

    def __init__(self, my_node):
        """ NodeCom initialization """

        Thread.__init__(self)

        # connected node
        self.my_node = my_node

        #-----Step 1: create TCP socket to signal presence to the node
        #print "Step 1"
        #f = file("Debug.txt", 'a')
        #f.write("Step 1\n")
        #f.close()
        # connection
        node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        node_socket.connect( (self.my_node.node_host, int(self.my_node.node_port)) )

        # create XMLRPC server
        while 1:
            try:
                #self.server =  SimpleXMLRPCServer( (self.my_node.my_host, self.my_node.my_port_node))
                self.server =  SimpleXMLRPCServer( addr=(self.my_node.my_host, self.my_node.my_port_node), logRequests=0)
                #print "SimpleXMLRPCServer()"
                #f = file("Debug.txt", 'a')
                #f.write("SimpleXMLRPCServer() OK\n")
                #f.close()
                break
            except:
                # may be the port is already used
                time.sleep(0.2)
                self.my_node.my_port_node = random.randint(1000,25000)
                #print "port for SimpleXMLRPCServer already used"
                #f = file("Debug.txt", 'a')
                #f.write("port for SimpleXMLRPCServer already used\n")
                #f.close()

        # send message
        msg = "openGUI;XML_RPC;"+str(self.my_node.my_host)+";"+str(self.my_node.my_port_node)
        node_socket.send(msg)
        #print "send openGUI msg"
        #f = file("Debug.txt", 'a')
        #f.write("send openGUI msg\n")
        #f.close()

        # waiting for answer
        answer = node_socket.recv(1024)
        node_socket.close()

        #-----Step 2: open an openGUI
        #print "Step 2 : [%s]" %answer
        #f = file("Debug.txt", 'a')
        #f.write("Step 2 return [" + answer+"] \n")
        #f.close()
        if answer and answer <> "refuse":

            # create client
            port_XML_GUI = string.split(answer,';')[1]
            host_XML_GUI = "http://" + self.my_node.node_host + ":" + port_XML_GUI

            self.client = xmlrpclib.Server(host_XML_GUI)
            #print "create xml rpc client (%s)" %host_XML_GUI

        #-----Step 3: open an OpenMedia
        #print "Step 3"
        # connection
        node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        node_socket.connect( (self.my_node.node_host, int(self.my_node.node_port)) )

        # send message
        msg = "openMedia;module2d_Chat;XML_RPC;"+str(self.my_node.my_host)+";"+str(self.my_node.my_port_node)+";1"
        node_socket.send(msg)
        #print "openMedia msg"

        # waiting for answer
        answer = node_socket.recv(1024)
        node_socket.close()
        #print "answer received : [%s]" %answer
        # ----------------------------------------

        self.alive = (answer and answer <> "refuse")


    def run(self):

        # attribute CallableFunction to server
        functions = CallableFunction(self.my_node)
        self.server.register_instance(functions)

        while self.alive:
            self.server.handle_request()
        #print 'End of XML Server ...'

        # -----------------------------------------


    def getInfos(self, id, var, addVar):
        return self.client.getInfos(id, var, addVar)


    def kill (self,auto = 0):
        self.alive = 0
        my_url = 'http://%s:%s'% (self.my_node.my_host,self.my_node.my_port_node)
        self.myclient = xmlrpclib.Server(my_url)
        if auto == 1:
            self.myclient.Null()

        return 1

    def kill(self):
        """ kill XML Server thread"""

        #print "connection.kill()"
        self.alive = 0

        # send a connection message in order to block out "accept" function
        kill_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        i = 1
        while 1:
            try:
                kill_sock.bind( (self.my_node.my_host, self.my_node.my_port_node + i) )
                break
            except:
                i += 1
        kill_sock.connect( (self.my_node.my_host, self.my_node.my_port_node) )
        kill_sock.close()

    def killAllThread(self):
        """ kill all thread """

        # kill XML Server thread
        self.kill()

        # kill all services
        # DEB SUP MCL
        #for service in self.my_node.services.values():
        #    service.kill()

        # send a message to the socket before quiting in order to kill chat service
        #killSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        #killSocket.bind( (self.my_node.my_host,self.my_node.my_port_node) )
        #killSocket.sendto( "KILL", (self.my_node.my_host, self.my_node.my_port_node +1 ) )
        #killSocket.close()
        # FIN SUP MCL

# ********************************************************************************
# --------------------------------------------------------------------------------
#               MY NODE
# --------------------------------------------------------------------------------
# ********************************************************************************


class MyNode:
    """ all information about my node """

    def __init__(self, node_host, node_port, navigator):
        """ node initialisation """

        #self.mutex = Lock()

        # network informations on Solipsis_Node
        self.node_host = node_host
        self.node_port = node_port

        # navigator attached to the node
        self.navigator = navigator

        # network informations on media module
        # DEB MOD MCL
        #self.my_host = socket.gethostbyname(socket.gethostname())
        self.my_host = node_host
        # FIN MOD MCL
        self.my_port_node = random.randint(1000,25000)

        # node characteristics
        self.id = 'me'
        self.pseudo = 'me'
        self.posX = 1
        self.posY = 1
        self.ar = 1
        self.ca = 1
        self.ori = 0

        # list of my neighbors
        # {id: object, ...}
        self.neighbors = {}

        # list of my_service
        # {id_service : object, ...}
        self.services = {}

    def launchConnection(self):
        """ start the connection with the node """

        #try:
        # ask for the connexion
        #print "enter in launchConnection"
        self.com = NodeCom(self)
        #print "NodeCom OK"
        self.com.start()
        #print "com start()"

        #except:
        #    sys.stderr.write("EXCEPTION : Can't join the node for starting connection\n")
                #f = file("Debug.txt", 'a')
                #f.write("EXCEPTION : Can't join the node for starting connection\n")
                #f.close()

    def getInfos(self):
        """ get information about the node we are connected """
        #print "connection.getInfos()"
        #f = file("Debug.txt", 'a')
        #f.write("connection.getInfos()\n")
        #f.close()
        #try:
        self.com.client.getInfos("module2d_Chat", "ALL", "0")
        #print "getInfos() OK"

        #except:
        #    sys.stderr.write("EXCEPTION : Can't join the node for getting information\n")
                #f = file("Debug.txt", 'a')
                #f.write("EXCEPTION : Can't join the node for getting information\n")
                #f.close()

    def addChatService(self):
        """ inform the node we have the chat service """
        #print "connection.addChatService"
        #try:
        self.com.client.addService("module2d_Chat", "Chat", "0", self.my_host ,str(self.my_port_node+1))
        #except:
        #    sys.stderr.write("EXCEPTION : Can't join the node for adding chat service\n")

    def addDisplay2dService(self):
        """ inform the node we have the chat service """
        #print "connection.addDisplay2dService"
        #try:
        self.com.client.addService("module2d_Chat", "Display2d", "0", self.my_host ,str(self.my_port_node+2))
        #except:
        #    sys.stderr.write("EXCEPTION : Can't join the node for adding display2d service\n")

    def closeConnection(self):
        """ close the connection with the node """
        #print "enter in closeConnection"
        #try:
        # close the media
        self.com.client.closeMedia('module2d_Chat')
        # close the GUI
        my_url = 'http://%s:%s'% (self.my_host, self.my_port_node)
        self.com.client.closeGUI(my_url)

        #except:
        #    sys.stderr.write("EXCEPTION : Can't join the node for closing connection\n")

        # kill all threads of the GUI
        self.com.killAllThread()

    def closeChatService(self):
        """ inform the node we no longer have the chat service """
        #print "connection.closeChatService"
        #try:
        self.com.client.closeService("module2d_Chat", "Chat")
        #except:
        #    sys.stderr.write("EXCEPTION : Can't join the node for closing chat service\n")

    def closeDisplay2dService(self):
        """ inform the node we no longer have the display2d service """
        #print "connection.closeDisplay2dService"
        #try:
        self.com.client.closeService("module2d_Chat", "Display2d")
        #except:
        #    sys.stderr.write("EXCEPTION : Can't join the node for closing display2d service\n")

    def kill(self):
        """ kill the node """
        #print "connection.kill()"
        try:
                # kill the node
            self.com.client.kill()

            # kill all threads of the GUI
            self.com.killAllThread()

        except:
            sys.stderr.write("EXCEPTION : Can't join the node for killing\n")

    def modSelf(self, var, delta):
        """ inform the node about its position modification"""
        #print "connection.modSelf()"
        try:
            self.com.client.modSelf(var, delta)
        except:
            sys.stderr.write("EXCEPTION : Can't join the node for modifying its position\n")

    def jump(self, x, y):
        """ inform the node about its jump position """
        debug.debug_info("connection.jump(" + str(x) + "," + str(y) + ")")
        self.com.client.jump(x, y)
        #try:
        #    self.com.client.jump(x, y)
        #except:
            #sys.stderr.write("EXCEPTION : Can't join the node for modifying its jump position\n")
        #    debug.debug_info("EXCEPTION : Can't join the node for modifying its jump position")

    def updatePos(self, delta_x, delta_y):
        """ update my coordinates and update neighbors' coordinates in accordance with my movement """
        debug.debug_info("connection.updatePos(%s,%s)" %(delta_x, delta_y))
        # we update posX and posY of my node with delta
        self.posX = long(self.posX + delta_x)
        self.posY = long(self.posY + delta_y)
        debug.debug_info("connection.updatePos() -> posX = [%d]" %self.posX)
        debug.debug_info("connection.updatePos() -> posY = [%d]" %self.posY)
        # we update positions of all neighbors in accordance with my movement
        for neighbors in self.neighbors.values():
            #self.mutex.acquire()
            neighbors.movePos(-delta_x,-delta_y)
            self.navigator.updateNeighbor(neighbors,-delta_x,-delta_y)
            #debug.debug_info("connection.updatePos -> call to wxPostEvent()")
            #wxPostEvent(self.navigator.ihm, wxMainFrame.updateNeighborEvent(neighbor=neighbors, delta_x=-delta_x, delta_y=-delta_y))
            #self.mutex.release()

    def updateAr(self, delta):
        """ we update the ar """

        self.ar = long(self.ar + delta)


    def updateCa(self, delta):
        """ we update ca  """

        self.ca += string.atol(delta)


    def updateOri(self, delta):
        """ we update ori """

        self.ori += long(delta)
