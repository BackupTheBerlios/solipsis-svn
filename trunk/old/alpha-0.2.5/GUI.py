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
## -----                           GUI.py                                   -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module involves :
##       - a thread that creates a socket TCP and listens for new connections.
##       Thus, Navigator may connect to this socket, notifying a protocol for the
##       interface. There could be an infinity of Interface.
##
##       - all functions callable by a Navigator. The interface module should
##       access to these functions, whatever the used protocol.
##
## ******************************************************************************

from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
import sys
import time

# Solipsis packages
import Communication
import Media
from Function import *
import globalvars

#################################################################################################
#                                                                                               #
#			-----  Thread for GUI modules connection ---------        		#
#                                                                                               # 
#################################################################################################

class GUI(Thread):

  def __init__(self, host, port, GUI_functions):
    Thread.__init__(self)

    # data
    self.host = host
    self.port = port
    self.GUI_functions = GUI_functions

    # if a receptive exists, a pointer, else null
    self.receptive_object = 0

    # open socket
    try:
      self.socket = socket(AF_INET, SOCK_STREAM)
      self.socket.bind( (self.host, self.port) )
    except:
      sys.stderr.write('port for GUI connection %s already used...' %str(self.port))
      globalvars.ALIVE = 0
      sys.exit(0)

    self.socket.listen(1)
      
#################################################
#              kill                             #
#################################################

  def kill(self):

    if self.receptive_object:
      try:
        self.receptive_object.kill()
      except:
        pass    

    # send a connection message in order to block out "accept" function
    kill_sock = socket(AF_INET, SOCK_STREAM)
    i = 1
    while 1:
      try:
        kill_sock.bind( (self.host, self.port + i) )
        break
      except:
        i += 1
    kill_sock.connect( (self.host, self.port) )
    kill_sock.close()

#################################################
#              run                              #
#################################################
    
  def run(self):
    """ Receive messages from the GUIs and process them"""

    while globalvars.ALIVE:

      # waiting for connection
      client_socket,client_address = self.socket.accept()

      # message reception
      msg = client_socket.recv(1024)
      
      if msg:

        # aliveness message
        if msg == "isAlive":
          client_socket.send("1")

        elif msg == "KILL":
          break

        else:
       
          # determine function
          func = msg.split(";")[0]
          
          if func == "openGUI":
            try:
              protocol, address, port = decodeMsg(msg)
              found_port = self.openGUI(protocol, address, port)
            except:
              sys.stderr.write('bad argument')
              found_port = 0

          elif func == "openMedia":
            try:
              id_media, protocol, address, port, pushOrPull = decodeMsg(msg)
              found_port = self.openMedia(id_media, protocol, address, port, pushOrPull)
            except:
              sys.stderr.write('bad argument')
              found_port = 0

          elif func == "isAlive":
            client_socket.send("1")

          else:
            sys.stderr.write('Error in message reception')
            found_port = 0

          # answer "accept;port" if a port has been found, "refuse" else
          if not found_port:
            message = "refuse"
            client_socket.send(message)
          else:
            message = encodeMsg(["accept", str(found_port)])
            client_socket.send(message)
          
      client_socket.close()
        
    # close socket
    self.socket.close()
    print "End of TCP connection..."
    
#################################################
#              openGUI                          #
#################################################

  def openGUI(self, protocol, address, port):
    """ a new Control Panel takes control of Node"""
    
    if not globalvars.me.GUIConnected:

      # indicating that a GUI is connected
      globalvars.me.GUIConnected = 1
      
      try:
        # launch a Receptive thread
        new_thread = Communication.Receptive_XML_RPC(self.host, self.port, self.GUI_functions)
        new_thread.start()
        self.receptive_object = new_thread

      except:
        globalvars.me.GUIConnected = 0
        sys.stderr.write('Protocol %s not supported' % str(protocol) )
	return 0

      return self.receptive_object.getPort()
    
    return 0

#################################################
#              openMedia                        #
#################################################

  def openMedia(self, id_media, protocol, address, port, pushOrPull):
    """ a new Media module is launched"""

    if globalvars.me.GUIConnected and not globalvars.me.media.has_key(id_media) and protocol == "XML_RPC":

      # accept new media and init it
      emissive_object = self.receptive_object.getClass(address, port)

      globalvars.me.media[id_media] = Media.Media(id_media, address, port, emissive_object, int(pushOrPull) )
	
      return self.receptive_object.getPort()
   
    return 0

#################################################################################################
#                                                                                               #
#			----- methods callable by GUI ---------					#
#                                                                                               #
#################################################################################################

class GUI_Functions:
  
  def __init__(self):
    pass

#################################################
#              isAlive                          #
#################################################
    
  def isAlive(self):
    """ Return 1"""
    
    return 1

#################################################
#              getValue                         #
#################################################

  def getValue(self, var):
    """ Return the value of the var"""
    
    if var == "AR":
      return str(globalvars.me.awareness_radius)
    elif var == "POS":
      return str(globalvars.me.position[0]) + ", " + str(globalvars.me.position[1])
    elif var == "PSEUDO":
      return globalvars.me.pseudo    
    elif var == "ORI":
      return globalvars.me.ori
    
#################################################
#              modSelf                          #
#################################################

  def modSelf(self, var , string_delta):
    """ movement (dX, dY) required by GUI"""

    if var == "POS" :
      delta = string_delta.split(',')
      globalvars.mutex.acquire()
      globalvars.me.updatePos(long(delta[0]), long(delta[1]))
      globalvars.mutex.release()
    elif var == "ORI":
      globalvars.mutex.acquire()
      globalvars.me.updateOri( long(string_delta) )
      globalvars.mutex.release()
    
    return 1
  
#################################################
#              getInfos                         #
#################################################

  def getInfos(self, id_media, var, add_var = 0):
    """ the media id_media asks informations on local world"""

    if not globalvars.me.media.has_key(id_media):
      return 0

    globalvars.mutex.acquire()

    # retrieve media instance
    media = globalvars.me.media[id_media].thread

    if var == "ALL":
      
      # send info about this node
      if media.init(globalvars.me.ident, globalvars.me.position[0], globalvars.me.position[1], globalvars.me.awareness_radius, globalvars.me.caliber, globalvars.me.pseudo, globalvars.me.ori) == -1:
	sys.sterr.write("error in init")
        if media.addBug():
          del globalvars.me.media[id_media]
      else:
        media.bug = 0

      time.sleep(0.3)

      # send data on neighbors
      for ent in globalvars.me.adjacents.values():
        if media.newNode(ent.id, ent.local_position[0], ent.local_position[1], ent.caliber, ent.pseudo,ent.ori) == -1:
          sys.stderr.write("error in New node at initialization")
          if media.addBug():
            del globalvars.me.media[id_media]
        else:
          media.bug = 0

    elif var == "ME":

      # send info about this node.
      if media.init(globalvars.me.ident, globalvars.me.position[0], globalvars.me.position[1], globalvars.me.awareness_radius, globalvars.me.caliber, globalvars.me.pseudo, globalvars.me.ori) == -1:
	sys.sterr.write("error in init")
        if media.addBug():
          del globalvars.me.media[id_media]
      else:
        media.bug = 0
          
    elif var == "SERVICE":

      # add_var = id_service
      for ent in globalvars.me.adjacents.values():
        if add_var in ent.services:
          if media.service(ent.id, id_service, ent.services[add_var][0], ent.services[add_var][1], ent.services[add_var][2]) == -1:
            sys.sterr.write("error in service")
            if media.addBug():
              del globalvars.me.media[id_media]
          else:
            media.bug = 0
              
    elif var == "ADJACENT":

      # add_var = ident
      if globalvars.me.adjacents.has_key(add_var):
        ent = globalvars.me.adjacents[add_var]
        if media.newNode(ent.id, ent.local_position[0], ent.local_position[1], ent.caliber, ent.pseudo, ent.ori) == -1:
          sys.sterr.write("error in newNode")
          if media.addBug():
            del globalvars.me.media[id_media]
        else:
          media.bug = 0

    globalvars.mutex.release()
    
    return 1
  
#################################################
#              closeMedia                       #
#################################################

  def closeMedia(self, id_media):
    """ media id_media has been closed"""
    
    if not globalvars.me.media.has_key(id_media):
      return 0

    # inform neighbors that services are now closed
    for id_service in globalvars.me.media[id_media].services.keys():
        msg = encodeMsg(["ENDSERVICE", globalvars.me.ident, id_service])
        for ent in globalvars.me.adjacents.values():
          ent.sendNetworkMessage(msg)
        
    del globalvars.me.media[id_media]
    return 1
  
#################################################
#              modMedia                         #
#################################################
    
  def modMedia(self, id_media, delta_percentage):
    """ modify the resource utilization of media id_media"""
    # TODO
    return 1
  
#################################################
#              addService                       #
#################################################
    
  def addService(self, id_media, id_service, desc_service, host, port):
    """ the media id_media owns a service id_service whose description is descr_service at host and port"""

    # update media informations
    try:
      media = globalvars.me.media[id_media]
    except:
      return 0
    media.services[id_service] = [desc_service, host, port]

    # send service to neighbors
    for ent in globalvars.me.adjacents.values():
      if ent.ok:
        msg = encodeMsg(["SERVICE", globalvars.me.ident, id_service, desc_service, host, port])
        ent.sendNetworkMessage(msg)

    # map neighbor services
    for ent in globalvars.me.adjacents.values():
      if id_service in ent.services:
        if media.thread.service(ent.id, id_service, ent.services[id_service][0], ent.services[id_service][1], ent.services[id_service][2]) == -1:
          sys.sterr.write("error in service")
          if media.addBug():
            del globalvars.me.media[id_media]
        else:
          media.bug = 0
        

    return 1

#################################################
#              closeService                     #
#################################################  
    
  def closeService(self, id_media, id_service):
    """ the media id_media closes the service id_service"""

    if globalvars.me.media.has_key(id_media) and globalvars.me.media[id_media].services.has_key(id_service):
     
      # send ENDSERVICE message to neighbors
      msg = encodeMsg(["ENDSERVICE", globalvars.me.ident, id_service])
      for ent in globalvars.me.adjacents.values():
        ent.sendNetworkMessage(msg)

      # delete service
      del globalvars.me.media[id_media].services[id_service]
      return 1
    
    else:
      
      return 0
    
#################################################
#              closeGUI                         #
#################################################     

  def closeGUI(self, url):
    """ GUI killed but node is still alive"""
    
    if not globalvars.me.GUIConnected:
      return 0

    globalvars.mutex.acquire()
    
    # Close all medias
    for media in globalvars.me.media.values():
      if not media.thread.close():
        sys.stderr.write("Error in Close")        

    # remove all occurences of media
    globalvars.me.GUIConnected = 0
    globalvars.me.media.clear()
    
    globalvars.mutex.release()
    
    return 1
  
#################################################
#              jump                             #
#################################################     

  def jump(self, x, y):
    """ teleportation to position (x, y)"""
    print "GUI.jump(%s, %s)" %(x,y)
    if not globalvars.me.GUIConnected:
      return 0
    
    # get further position
    posX = long(x)
    posY = long(y)
    print "GUI.posX=[%d]" %posX
    print "GUI.posY=[%d]" %posY
    
    # get network infos from one entity
    host = str(globalvars.me.distAdjacents.ll[0].host)
    port = int(globalvars.me.distAdjacents.ll[0].port)
    print "GUI.host=[%s]" %host
    print "GUI.port=[%s]" %port
    
    # close all connections
    for ent in globalvars.me.adjacents.values():
        ent.sendNetworkMessage(encodeMsg(["CLOSE", globalvars.me.ident]))
        closeConnection(ent)
    print "GUI.CloseConnection OK"
    # update positions and awareness radius
    globalvars.me.updatePos( (posX - globalvars.me.position[0]), (posY - globalvars.me.position[1]) )
    print "GUI.updatePos() OK"
    globalvars.me.updateAR(- globalvars.me.awareness_radius)
    print "GUI.updateAR() OK"
    # world entrance
    globalvars.me.worldEntrance(host,port)
    print "GUI.worldEntrance()"
    return 1
  
#################################################
#              kill                             #
#################################################     
  
  def kill(self):
    """ GUI can stop the entity
    The network socket is blocking, so it is necessary to send a specific message
    in order to quit """

    globalvars.ALIVE = 0
    
    # Kill all threads 
    killAllThread()
    
    return 1
    

