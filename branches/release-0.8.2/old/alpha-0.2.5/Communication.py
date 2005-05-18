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
## -----                           Communication.py                         -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is an interface for the communication between Node and Navigator
##   It uses XML-RPC.
##   It may be used as an example for future interfaces. It offers both
##   methods for emission of messages and reception of messages.
##   It relies on functions defined in GUI module.
##
## ******************************************************************************


from xmlrpclib import *
from SimpleXMLRPCServer import *
from threading import Thread

import globalvars

#################################################################################################
#                                                                                               #
#	       ----- thread for Reception of XML_RPC invocations from Modules Media ---------   #
#                                                                                               #
#################################################################################################

class Receptive_XML_RPC(Thread):
  def __init__(self, my_host, my_port, GUI_functions):
    Thread.__init__(self)
    
    self.host = my_host

    # server XMLRPC
    i = 0
    while 1:
      try:
        self.server =  SimpleXMLRPCServer((self.host, my_port + i))
        break
      except:
        i += 1

    self.port = my_port + i
      
    # functions callable by the GUI
    self.server.register_instance(GUI_functions)
    
# getPort --------------------

  def getPort(self):

    return self.port

# getClass --------------------

  def getClass(self, host, port):

    return Emissive_XML_RPC(host, port)
  
# kill --------------------

  def kill(self):
    
    # Send a message to awake it.
    try:
      url = str(self.host) + ":"+str(self.port)
      newServer = xmlrpclib.Server(url)
      newServer.isAlive()
    except :
      pass
    
# run --------------------    
  def run(self):
    """ Receive messages from the GUI and process them"""
    
    while globalvars.ALIVE:
      self.server.handle_request()
    print "End of Xml connection..."


##########################################################################################
#                                                                                        #
#          -------- Emission of XML_RPC invocations to Media Modules -------             #
#                                                                                        #
##########################################################################################

class Emissive_XML_RPC:
  def __init__(self, host, port):
    
    self.url = "http://" + host + ":" + str(port)
    try:
      self.server = xmlrpclib.Server(self.url)
    except :
      sys.stderr.write('error in XML_RPC init\n')
      
  def init(self, id, positionX, positionY, awareness_radius, caliber, pseudo, ori):
    """ Send message init"""
    
    try:
      return self.server.init(id, str(positionX), str(positionY), str(awareness_radius), str(caliber), pseudo, ori )
    except:
      return -1

  def newNode(self, id, positionX, positionY, caliber, pseudo,ori):
    """ Send a mesage newNode"""
    
    try:
      return self.server.newNode(id, str(positionX), str(positionY), str(caliber), pseudo ,str(ori) )
    except:
      return -1

  def close(self):
    """ Send a message close"""
    
    try:
      return self.server.close()
    except:
      return -1

  def modNode(self, id, stringVar, stringVariation):
    """ Send a mesage modNode"""
    
    try:
      return self.server.modNode(id, stringVar, stringVariation)
    except:
      return -1

  def modSelf(self, var, string_variation):
    """ Send a message modSelf"""
    
    try:
      return self.server.modSelf(var, string_variation)
    except:
      return -1

  def deadNode(self, id):
    """ Send a message deadNode"""
   
    try:
      return self.server.deadNode(id)
    except:
      return -1
    
  def service(self, id, id_service, desc, host, port):
    """ Send a message service"""

    try:
      return self.server.service(id, id_service, desc, host, port)
    except :
      return -1

  def closeService(self, id, id_service):
    """ Send a message closeService"""

    try:
      return self.server.closeService(id, id_service)
    except :
      return -1    
