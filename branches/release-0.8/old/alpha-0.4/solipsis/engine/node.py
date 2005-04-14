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
## -----                           node.py                                   -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module defines the class for self informations.
##   It provides the definition of the entity, the methods for the node connection
##   and the methods for the modifications of the variable characteristics.
##
## ******************************************************************************


import sys, time

import ConfigParser, logging, logging.config
from Queue import Queue

from solipsis.util.parameter import Parameters
from solipsis.util.util import Geometry, NotificationQueue
from solipsis.util.exception import SolipsisConnectionError

from solipsis.engine.entity import Entity
from solipsis.engine.peer import PeersManager
from solipsis.engine.connector import UDPConnector, XMLRPCConnector
from solipsis.engine.engine import V0_2_5_Engine
from solipsis.engine.control import ControlEngine, InternalEngine

class Node(Entity):
  
  def __init__(self, params):
    """ All informations about this node:
    host --> ip if the node, network_port, GUI_port, posX, posY, ar, ca, 
    ori --> a point, 
    exp --> expected number of neighbour, pseudo"""


    # event queue, used for inter-thread communication
    self.events = NotificationQueue()

    # network communication with peers is handled by this object
    netParams = params.getNetParams()
    self.peerConnector = UDPConnector("peer", self.events, netParams)

    controlParams = params.getControlParams()
    self.controlConnector = XMLRPCConnector("control", self.events, controlParams)

    # set the solipsis protocol used
    engineParams = params.getEngineParams()
    self.engine = V0_2_5_Engine(self, engineParams)

    self.controlEngine = ControlEngine(self, engineParams)
    self.internalEngine = InternalEngine(self, engineParams)
    
    position = [params.posX, params.posY]
    
    # call parent class constructor
    Entity.__init__(self, position, params.ori, params.ar, params.caliber,
                  params.pseudo)
    
    self.id = "unknown"
    
    # maximum expected number of neighbours.
    self.exp = params.exp
    
    # our IP address or 'localhost' if not specified in config file
    self.host = params.host
    
    self.alive = True
    self.logger = params.rootLogger
    
    # manage all peers
    peersParams = params.getPeersParams()
    self.peersManager = PeersManager(self, peersParams)

    # set world size in Geometry class
    Geometry.SIZE = params.world_size
    self.params=params
   
  def getPeersManager(self):
    return self.peersManager

  def updatePosition(self, newPosition):
    """ update the position of the node
    newPosition : the new poition of the node , a list [posX, posY]
    """
    self.node.position = newPosition
    manager = self.getPeersManager()
    # re compute all positions of neighbours
    manager.update()
    

  def send(self, peer, message):
    """
    Send a message to a peer
    message : a solispsis message, e.g. 'HEARTBEAT;10.193.161.35:33363'
    peer    : a Peer object resenting the recipient of the message
    """
    #netEvent = NetworkEvent(message)
    #netEvent.setRecipient(peer.getNetAddress())
    #self.net.send(netEvent)
    self.peerConnector.send(peer, message)

  def sendController(self, message):
    self.controlConnector.send(message)
    
  def enterSolipsis(self):
    """
    Enter Solipsis world, we consider that we have entered solipsis as soon as have
    we are connected to one Solipsis entity
    Raise: SolipsisConnectionError when a timeout expires
    Return : True if the connection succeded
    """
    time_stamp = time.time()
    #message = "KNOCK;SOLIPSIS 0.3"
    message = "HI"
    timeout = self.params.connection_timeout
    
    while True:

      # retrieve peer
      manager = self.getPeersManager()
      peer = manager.getRandomPeer()
            
      # send message  
      self.send(peer, message)      
      time.sleep(0.5)

      # we got an answer, for one of our Hi messages: we have entered Solipsis 
      if not self.events.empty():
        self.alive = True
        return True

      # Time out : impossible to connect
      if time.time() > time_stamp + timeout:
        self.logger.critical("Time out: cannot connect to Solipsis")
        raise SolipsisConnectionError()

  def exit(self):
    """ stop the node and exit
    """
    # stop the network thread
    self.peerConnector.stop()

    # we do not need to stop the controlConnector. The controlConnector
    # stopped after sending us the exit message
    # --> self.controlConnector.stop() not needed !
    
    # wait for the other threads before exiting
    self.peerConnector.join()
    self.controlConnector.join()

    self.alive = False
    
  def mainLoop(self):
    """ Main loop of the program """
    # start control connector
    self.controlConnector.start()
    # start peer connector
    self.peerConnector.start()

    try:
      # enter solipsis : send the first message
      #self.enterSolipsis()
      pass
    except:
      self.logger.critical("cannot enter Solipsis, exiting...")
      self.exit()
      raise

    while self.alive:
      self.events.acquire()
      # no events to process - wait for a notification from other threads
      if self.events.empty():
        self.events.wait()
        
      # We can immediately release the lock: we know that there is an item available
      # because this is the only thread that consumes items from the queue.
      # If other threads can consume item then we must first get the item then
      # release the lock
      self.events.release()
      
      # process one event in queue        
      event = self.events.get()
      
      type = event.type()
      #self.logger.debug("%s - %s - %s ", event.name(), event.type(),
      #                  event.data())
      if( type == Event.PEER ):
        self.engine.process(event)
      elif( type == Event.CONTROL):
        self.controlEngine.process(event)
      elif type == Event.INTERNAL:
        self.internalEngine.process(event)
      else:
        self.logger.critical("Unknown event type" + type)
                      
    self.logger.debug("end of main loop")
    
  def processPeriodicEvent(self, event):
    """ Process periodic tasks
    Send heartbeat message
    Or check global connectivity
    """
    # TO DO
    self.logger.critical("processPeriodicEvent not implemented")
