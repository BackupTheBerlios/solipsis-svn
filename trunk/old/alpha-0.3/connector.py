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
## -----                           connector.py                               -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   The concern of this module is to allow the node to communicate with its
##   neighbor in order to form the netork of peers.
##   It allows the creation of a socket UDP for the message exchange
##   It provides all treatments for each message reception.
##
## ******************************************************************************

from threading import Thread
#import string, sys, logging
import sys, time
from Queue import Queue
from socket import socket, AF_INET, SOCK_DGRAM
import select
from SimpleXMLRPCServer import SimpleXMLRPCServer
from control import ControlEngine

from event import PeerEvent, ControlEvent
from util import NotificationQueue

class Connector(Thread):
  """ Generic class for connecting to an entity """
  def __init__(self, type, eventQueue):
    """ Constructor
    type : type of connector - 'peer' or 'control'
    eventQueue : queue used to communicate with other thread. The PeerConnector
    fills this queue with events. Other threads are responsible for reading and
    removing events from this queue
    """
    Thread.__init__(self)
    
    # Event queue used to communicate with other threads
    self.incoming = eventQueue

    # Message to send queue
    self.outgoing = NotificationQueue()
    
    # this flag is set to True when we want to stop this thread
    self.stopThread = False

    # type of connector, can be a "peer" or "control"
    self.type = type
    
  def stop(self):
    """ Stop the network thread
    """
    self.stopThread = True

  def setType(self, newType):
    """ Set the connector type.
    newType: new type of the connector """
    self.type = newType
    
class UDPConnector(Connector):
  """ Connection to peers using UDP sockets """  
  def __init__(self, type, eventQueue, netParams):
    """ Constructor.
    ype : type of connector - 'peer' or 'control'
    eventQueue : queue used to communicate with other thread. The PeerConnector
    fills this queue with events. Other threads are responsible for reading and
    removing events from this queue
    netParams : initialization parameters of this class -
    a list [ buffer_size, logger_object ]
    """
    Connector.__init__(self, type, eventQueue)

    [self.BUFFER_SIZE, self.logger] = netParams
    
    # network socket
    self.socket = socket(AF_INET, SOCK_DGRAM)
    self.socket.setblocking(0)
    

  def run(self):
    """ Receive messages from other nodes and process them.
    Send messages to other nodes.
    """

    while not self.stopThread:

      # send outgoing messages
      if not self.outgoing.empty():
        e = self.outgoing.get()
        self._send_no_wait(e)

      readsock, writesock, errsock = select.select([self.socket], [], [],0)

      if len(readsock):
        try:
          # receive and process message from other nodes        
          data, sender = self.socket.recvfrom(self.BUFFER_SIZE)
          self.logger.debug("recvfrom %s", data)
          
          # store raw network message and
          # store the type of the event, the connector knows what kind of event
          # we received, either a "peer" or a "control" event
          netEvent = NetworkEvent(self.type, data)
          # store ip address and port of sender
          netEvent.setSender(sender)
          
          # add a new event to the queue of events that need to be processed
          self.incoming.put(netEvent)
        except ValueError:
          self.logger.warn("NetThread - parsing error - unknown message " + data)
        except:
          self.logger.debug("Exception in network thread - " +
                            str(sys.exc_info()[0]))
          raise
          time.sleep(0.2)

        
      
        #raise
        #break
    # close socket        
    self.socket.close()
    self.logger.info('End of Network Server...')

  def send(self, peer, msg):
    """ Send a message to a peer
    To avoid problems when different thread access the socket object, only the
    network thread can send messages. As this method can be called by other
    threads, the message is NOT sent here. The message is instead added to a
    queue, and will be sent later by the network thread
    """
    netEvent = NetworkEvent(self.type, msg)    
    netEvent.setRecipient(peer.getNetAddress())
    self.outgoing.put(netEvent)

  def _send_no_wait(self, netEvent):
    """ Send a message
    Immediatly send a message. This method must only be called from the network
    thread.
    """
    try:
      host, port =  netEvent.recipient()
      data = netEvent.data()
      self.logger.debug("_send_no_wait %s %d - %s", host, port, data)
      self.socket.sendto(netEvent.data(), (host, port))
    except:
      self.logger.critical("Error while sending %s %s %d", data, host, port)
      raise

  def encodeMsg(self, list):
    """ encode list of string list and return a string"""
    return ";".join(list)


class XMLRPCConnector(Connector):
  def __init__(self, type, eventQueue, controlParams):
    """ Constructor.
    eventQueue : queue used to communicate with other thread. The PeerConnector
    fills this queue with events. Other threads are responsible for reading and
    removing events from this queue
    netParams : initialization parameters of this class -
    a list [ buffer_size, logger_object ]
    """
    Connector.__init__(self, type, eventQueue)
    [self.host, self.port, self.logger] = controlParams
    # standard response for non get queries
    self.ok = "1"
    
  def run(self):    
    self.server =  SimpleXMLRPCServer((self.host, self.port))
    self.server.register_instance(self)
    
    while not self.stopThread:
      self.server.handle_request()

    self.logger.info("End of control thread")
    
  def send(self, message):
    self.outgoing.put(message)
  
  def update(self, var, value):
    """ Update a caracteristic of the node
    var : the type of information to update, 'AR', 'POS', 'ORI', 'PSEUDO'
    value : new value
    """
    #controlEvent = UpdateEvent(var, value)
    controlEvent = ControlEvent(["update", var, value])
    self.incoming.put(controlEvent)
    return self.ok
  
  def getNodeInfo(self, navId):
    """ Return all the caracteristics of the node
    [id, positionX, positionY, AR, CA, pseudo, orientation ]
    navId : ID of the navigator asking this information
    """
    controlEvent = ControlEvent(["nodeinfo", navId])
    self.logger.debug("getnodeinfo "+str(navId))
    self.incoming.put(controlEvent)
    return self.waitAndReply()

  def getPeerInfo(self, navId, id):
    """ Return all the caracteristics of a peer
    [id, positionX, positionY, AR, CA, pseudo, orientation ]
    navId : id of the navigator
    id : id of the peer
    """
    controlEvent = ControlEvent(["peer", id])
    self.incoming.put(controlEvent)
    return self.waitAndReply()


    
  def getAllPeers(self):
    controlEvent = ControlEvent(["peers"])
    self.incoming.put(controlEvent)
    return self.waitAndReply()

  def connect(self):
    """ Connect to solipsis. """
    controlEvent = ControlEvent(["connect"])
    self.incoming.put(controlEvent)
    # return "OK" or "NOK" if node cannot connect
    return self.waitAndReply()

  def disconnect(self):
    """ Disconnect node
    Return OK """
    controlEvent = ControlEvent(["disconnect"])
    self.incoming.put(controlEvent)
    return self.ok
    
  def addService(self, srvId, srvDesc, srvConnectionString):
    """ add a new service to the node. """
    service = ControlEvent(["service", srvId, srvDesc, srvConnectionString])
    self.incoming.put(service)
    return self.ok

  def removeService(self, srvId):
    """ Remove a service
    srvId : id of the service to remove
    Return : OK """
    service = ControlEvent(["removeservice", srvId])
    self.incoming.put(service)
    return self.ok

  def startNode(self, navId):
    """ Start the node.
    navId : ID of the navigator."""
    start = ControlEvent(["start", navId])
    self.incoming.put(start)
    return self.waitAndReply()

  def kill(self, navId):
    """ Kill the node and stop connection betwwen navigator and node
    navId : ID of the navigator.
    """
    kill = ControlEvent(["kill", navId])
    self.incoming.put(kill)
    self.stop()
    #return self.waitAndReply()
    return self.ok
    
  def waitAndReply(self):  
    """ wait for notification from main thread """
    self.outgoing.acquire()
    if self.outgoing.empty():
      self.outgoing.wait()

    self.outgoing.release()
    
    e = self.outgoing.get()
    response = e.data()
    return response

  
