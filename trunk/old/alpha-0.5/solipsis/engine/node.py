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

from solipsis.engine.entity import Entity, Position, Address
from solipsis.engine.peer import PeersManager
from solipsis.engine.connector import UDPConnector, XMLRPCConnector, InternalConnector
import state
#from solipsis.engine.engine import V0_2_5_Engine
#from solipsis.engine.control import ControlEngine, InternalEngine

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

    intParams =  params.getInternalParams()
    self.internalConnector = InternalConnector('internal', self.events, intParams)
    
    position = Position(params.posX, params.posY)
    
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

    self.state = None
    self.setState('NotConnected')
    
  def getPeersManager(self):
    return self.peersManager

  def setState(self, stateClass):
    stmt = 'state.' + stateClass + '(self, self.logger)'
    try:
      self.state = eval(stmt)
    except:
      raise SolipsisInternalError('unknown state ' + stateClass)

  def fire(self, event):
    """ Send an event.
    event : the event to send.
    """
    connector = None
    type = event.getType()
    if type == 'peer':
      connector = self.peerConnector
    elif type == 'control':
      connector = self.controlConnector
    elif type == 'internal':
      connector = self.internalConnector
    else:
      raise SolipsisInternalError('Unknown event type ' + type )
    
    connector.send(event)
    
  def exit(self):
    """ stop the node and exit
    """
    # stop the network thread
    self.peerConnector.stop()
    self.internalConnector.stop()    
    # we do not need to stop the controlConnector. The controlConnector
    # stopped after sending us the exit message
    # --> self.controlConnector.stop() not needed !
    
    # wait for the other threads before exiting
    self.peerConnector.join()
    self.controlConnector.join()
    self.internalConnector.join()
    self.alive = False
    
  def mainLoop(self):
    """ Main loop of the program """
    # start control connector
    self.controlConnector.start()
    # start peer connector
    self.peerConnector.start()
    # start internal connected : needed for periodic tasks
    self.internalConnector.start()
    

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
      request = event.getRequest()

      try:
        # process this request according to our current state
        # e.g.: stmt='self.state.NEAREST(event)'
        stmt = 'self.state.' + request + '(event)'
        eval(stmt)
      except:
        self.logger.debug(sys.exc_info()[0])
        self.logger.debug(sys.exc_info()[1])
        self.logger.debug("unknown request "+ stmt)
                                 
    self.logger.debug("end of main loop")
    
 
