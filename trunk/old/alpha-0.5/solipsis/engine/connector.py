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

from threading import Thread, Timer
import sys, time, select
from Queue import Queue
from socket import socket, AF_INET, SOCK_DGRAM
from SimpleXMLRPCServer import SimpleXMLRPCServer

from solipsis.engine.event import PeerEvent, ControlEvent
from solipsis.util.util import NotificationQueue

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
    type : type of connector - 'peer' or 'control'
    eventQueue : queue used to communicate with other thread. The PeerConnector
    fills this queue with events. Other threads are responsible for reading and
    removing events from this queue
    netParams : initialization parameters of this class -
    a list [ buffer_size, logger_object ]
    """
    Connector.__init__(self, type, eventQueue)

    [self.BUFFER_SIZE, self.logger, self.host, self.port] = netParams
    
    # network socket
    self.socket = socket(AF_INET, SOCK_DGRAM)

    # If optionnal parameters IP address and port are supplied, bind socket to
    # this network address
    if self.host is not None and self.port is not None:
      self.socket.bind((self.host, self.port))

    self.socket.setblocking(0)
    self.logger.debug("UDP connector started:" + str(self.socket.getsockname()))

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

          # Parse data and create a new event
          netEvent = EventParser().createEvent(data)
          netEvent.setType(self.type)
          
          # store ip address and port of sender
          netEvent.setSenderAddress(Address(sender[0], sender[1]))
          
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

  def send(self, netEvent):
    """ Send a message to a peer
    To avoid problems when different thread access the socket object, only the
    network thread can send messages. As this method can be called by other
    threads, the message is NOT sent here. The message is instead added to a
    queue, and will be sent later by the network thread
    """
    self.outgoing.put(netEvent)

  def _send_no_wait(self, netEvent):
    """ Send a message
    Immediatly send a message. This method must only be called from the network
    thread.
    """
    try:
      address =  netEvent.getRecipientAddress()
      host = address.getHost()
      port = address.getPort()

      data = EventParser(netEvent).data()
      self.logger.debug("_send_no_wait %s %d - %s", host, port, data)
      self.socket.sendto(netEvent.data(), (host, port))
    except:
      self.logger.critical("Error while sending %s %s %d", data, host, port)
      raise


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
    [self.host, self.controlPort,
     self.notificationPort, self.logger] = controlParams
  
  def run(self):
    """ Start 2 XML/RPC servers one for receiving control message from the
    controller and another to send both reply to queries and asynchronous events
    coming from the network (e.g. this 2nd channel is used to notify the
    controller when a new node is discovered) """
    
    # XML/RPC server used for receiving control orders
    self.controlChannel = XMLRPCControlChannel(self.host, self.controlPort)
    # XML/RPC server used for sending notification to the controller
    self.notificationChannel = XMLRPCNotificationChannel(self.host,
                                                         self.notificationPort)    
    self.notificationChannel.start()
    
    while not self.stopThread:
      self.controlChannel.server.handle_request()
      
    # set the STOP flag of the notification thread
    self.notificationChannel.stopThread = True
    # we need to send back the kill event to the controller because he is waiting
    # for a reply from the notification thread
    # (the call to XMLRPCNotificationChannel.get is blocking)
    self.send(Event(["kill"]))
                             
    # wait for child thread before exiting 
    notificationChannel.join()
    self.logger.info("End of control thread")
    
  def send(self, message):
    """ Send a message to the controller"""
    self.notificationChannel.send(message)
    
class XMLRPCNotificationChannel(Thread):
  """ Comunication channel used by the node to send notification to its controller.
  It is a one-way communication channel from the node to the controller.
  The controller calls the get method, and blocks waiting for a reply. Whenever a
  new event needs to be sent to the controller, this message is sent back in reply
  to the get method call and the controller calls back the get method.  
  """
    
  def __init__(self,host, port):
    """ Constructor.
    host : ip address of the node
    port : port used by this XML/RPC server"""
    Thread.__init__(self)
    self.host = host
    self.port = port
    self.server =  SimpleXMLRPCServer((self.host, self.port))
    self.server.register_instance(self)
    self.stopThread = False
    

    # Message to send queue
    self.outgoing = NotificationQueue()
    
    # this flag is set to True when we want to stop this thread
    self.stopThread = False
    
  def run(self):
    while not self.stopThread:
      self.server.handle_request()

  def get(self):
    """ Wait for notification from the node main thread and send back events to the
    controller. The controller calls the get method and is notified when a network
    event occurs."""
    # get the lock
    self.outgoing.acquire()
    # nothing to send, just wait
    if self.outgoing.empty():
      self.outgoing.wait()

    # the main thread called the notify method to awaken this thread
    # release the lock and send back the message to the controller.
    self.outgoing.release()
    
    e = self.outgoing.get()
    response = e.data()
    return response
    
  def send(self, message):
    """ Send a message to the controller"""
    self.outgoing.put(message)
  
  
  

class XMLRPCControlChannel:
  """ Channel used for receiving orders from a navigator

  """
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.server = SimpleXMLRPCServer((self.host, self.port))
    self.server.register_instance(self)
    
    # standard response for non get queries
    self.ok = "1"

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
    #return self.waitAndReply()
    return self.ok

    
  def getAllPeers(self):
    controlEvent = ControlEvent(["peers"])
    self.incoming.put(controlEvent)
    #return self.waitAndReply()
    return self.ok

  def connect(self):
    """ Connect to solipsis. """
    controlEvent = ControlEvent(["connect"])
    self.incoming.put(controlEvent)
    return self.ok

  def disconnect(self):
    """ Disconnect node
    Return OK """
    controlEvent = ControlEvent(["disconnect"])
    self.incoming.put(controlEvent)
    return self.ok
    
  def startNode(self, navId):
    """ Start the node.
    navId : ID of the navigator."""
    start = ControlEvent(["start", navId])
    self.incoming.put(start)
    #return self.waitAndReply()
    return self.ok
  
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

class InternalConnector(Connector):
  """ Management task (e.g. Timers) are scheduled through this connector """
  def __init__(self, type, eventQueue, internalParams):
    """ Constructor.
    type : type of connector - 'peer' or 'control'
    eventQueue : queue used to communicate with other thread. The PeerConnector
    fills this queue with events. Other threads are responsible for reading and
    removing events from this queue
    netParams : initialization parameters of this class -
    a list [ buffer_size, logger_object ]
    """
    Connector.__init__(self, type, eventQueue)

    [self.logger] = internalParams
    
    self.logger.debug("Internal connector started")

  def run(self):

    while not self.stopThread:
      t = Timer(5, self.kill)
      t.start()

      t.join()
      # thread for heartbeat messages
      #t = Timer(heartbeatInterval, self.heartbeat())
      #t.start()
      
      # thread for global connectivity checks


      # thread for adjacent policy and awareness radius management


      # thread for file entities.met management

      # statistics thread

  def heartbeat(self):
    evt = InternalEvent('SENDHEARTBEAT')
    self.incoming.put(evt)

  def kill(self):
    evt = ControlEvent('KILL')
    self.incoming.put(evt)
      
