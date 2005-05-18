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
## -----                           engine.py                               -----
## ------------------------------------------------------------------------------



import re
from threading import Thread
from Queue import Queue
from socket import socket, AF_INET, SOCK_DGRAM

from solipsis.engine.peer import Peer
from solipsis.util.event import PeerEvent
from solipsis.util.util import Geometry
from solipsis.util.exception import SolipsisInternalError
from solipsis.util.exception import SolipsisMessageParsingError

  
class Protocol:
  def __init__(self, _node, params):
    """ Constructor.
    node: the node associated with this engine"""
    logger = params[0]
    self.node = _node
    
    # all the possible states of the node
    self.state = State("NOT_CONNECTED")

    # version of the protocol
    self.version = "SOLIPSIS/1.0"
    
class MessageFactory:
  """ Class used for creating Solipsis messages.
  best, service, endservice, connect, hello, close, update, heartbeat
   around, queryaround, detect, search, found, findnearest, nearest
  """

  theFactory = None
  
  def __init__(self, node):
    """ Internal method, this class should only be called by the init method
    Constructor: create a Message factory object.
    node: the node which creates message through this factory
    """
    if MessageFactory.theFactory is not None:
      raise SolipsisInternalError("Error: Message factory object should only be " +
                                  "accessed through the getInstance method"  )
    self.node = node
    
  def getInstance():
    """ Static method.
    Return the message factory object. The same object is returned even if
    this method is called multiple times
    Raises: SolipsisInternalError if factory class is not initialized before using
    this method (MessageFactory.init must first be called)"""
    if MessageFactory.theFactory is not None:
      return  MessageFactory.theFactory
    else:
      raise SolipsisInternalError("Error: trying to use a non initialialized " +
                                  "message factory. MessageFactory.init(node) " +
                                  " must be called first")

  def init(node):
    """ Static method
    Initilization of the factory, this method must be called before using the
    factory
    """
    if MessageFactory.theFactory is None:
      MessageFactory.theFactory = MessageFactory(node)

  init = staticmethod(init)
  getInstance = staticmethod(getInstance)

  def _addRemoteEntityInfosHeaders(self, msg, peer):
    """ Internal method.
    Add all the entity infos headers of a peer to a message:
    'Remote-Address', 'Remote-Id', 'Remote-Position',
    'Remote-AwarnessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
    msg : the message to modify
    peer : The peer object used to fill-in the headers
    """    
    msg.addHeader('Remote-Address', peer.getAddress())
    msg.addHeader('Remote-Id', peer.getId())
    msg.addHeader('Remote-Position', peer.getStringPosition())
    msg.addHeader('Remote-AwarnessRadius', peer.getAwarenessRadius())
    msg.addHeader('Remote-Calibre', peer.getCalibre())
    msg.addHeader('Remote-Orientation', peer.getOrientation())
    msg.addHeader('Remote-Pseudo', peer.getPseudo())

  def _addEntityInfosHeaders(self, msg):
    """ Internal method.
    Add all the entity infos headers to a message: 'Address', 'Id', 'Position',
    'AwarnessRadius', 'Calibre', 'Orientation', 'Pseudo'
    msg : the message to modify
    """    
    msg.addHeader('Address', self.node.getAddress())
    msg.addHeader('Id', self.node.getId())
    msg.addHeader('Position', self.node.getStringPosition())
    msg.addHeader('AwarnessRadius', self.node.getAwarenessRadius())
    msg.addHeader('Calibre', self.node.getCalibre())
    msg.addHeader('Orientation', self.node.getOrientation())
    msg.addHeader('Pseudo', self.node.getPseudo())
      
  def createBestMsg(self):
    """ Create a BEST message. This is the reply to a FINDNEAREST message.
    I'm the closest node to a target position send all  my characteristics:
    Headers: 'Address', 'Id', 'Position','AwarnessRadius', 'Calibre',
    'Orientation', 'Pseudo'
    """
    msg = Message()
    msg.setMethod('BEST')
    self._addEntityInfosHeaders(msg)
    return msg

  def createConnectMsg(self):
    """ Create a CONNECT message. This is the reply to a HELLO message.
    Connect to a new peer. Send peer  all my characteristics.
    Headers: 'Address', 'Id', 'Position','AwarnessRadius', 'Calibre',
    'Orientation', 'Pseudo'
    """
    msg = Message()
    msg.setMethod('CONNECT')
    self._addEntityInfosHeaders(msg)
    return msg

  def createHelloMsg(self):
    """ Create a HELLO message. Propose a connection to a new peer. Send peer  all
    my characteristics.
    Headers: 'Address', 'Id', 'Position','AwarnessRadius', 'Calibre',
    'Orientation', 'Pseudo'
    """
    msg = Message()
    msg.setMethod('HELLO')
    self._addEntityInfosHeaders(msg)
    return msg

  def createFindnearestMsg(self):
    """ Create a FINDNEAREST message. We are looking for the peer that is the
    closest to a target postion.
    Headers: 'Position'    
    """
    msg = Message()
    msg.setMethod('FINDNEAREST')
    msg.addHeader('Position', self.node.getStringPosition())
    return msg
  
  def createServiceMsg(self, serviceId):
    """ Create a SERVICE message. Send peer a description of the services available
    for this node.
    Headers: 'Id', 'ServiceId', 'ServiceDesc', 'ServiceAddress'
    """
    msg = Message()
    msg.setMethod('SERVICE')
    srv = self.node.service[service_id]
    msg.addHeader('Id', self.node.id)
    msg.addHeader('ServiceId', serviceId)
    msg.addHeader('ServiceDesc', srv.desc)
    msg.addHeader('ServiceAddress', srv.address)
    return msg

  def createEndserviceMsg(self, serviceId):
    """ Create and ENDSERVICE message. This message is used to notify peers that
    a  service is no longer available.
    serviceIdc : the id of the service that is no longer available."""
    msg = Message()
    msg.setMethod('ENDSERVICE')
    msg.addHeader('Id', self.node.id)
    msg.addHeader('ServiceId', serviceId)
    return msg
  
  def createCloseMsg(self):
    """ Create a CLOSE message. Close connection with a peer.
    Headers: 'Id'
    """
    msg = Message()
    msg.setMethod('CLOSE')
    msg.addHeader('Id', self.node.id)
    return msg
  
  def createUpdateMsg(self):
    """ Message used to notify peers that one of our characteristics has changed
    name: name of the fied that changed. 'POS' or 'PSEUDO' or 'AR' or 'ORI' or
    'CAL' or 'PSEUDO'
    Headers : 'id' and ( 'Position' or 'Orientation' or 'AwarnessRadius' or
    'Calibre' or 'Pseudo' )
    """
    msg = Message()
    msg.setMethod('UPDATE')
    self._addEntityInfosHeaders(msg)
    """
    msg.addHeader('Id', self.node.getId())
    if ( name == "POS" ):      
      msg.addHeader('Position', self.node.getStringPosition())
    elif ( name == "ORI" ):
      msg.addHeader('Orientation', self.node.getOrientation())
    elif ( name == "AR"):
      msg.addHeader('AwarnessRadius', self.node.getAwarenessRadius())
    elif ( name == "CAL"):
      msg.addHeader('Calibre', self.node.getCalibre())
    elif ( name == "PSEUDO"):
      msg.addHeader('Pseudo', self.node.getPseudo())
    else:
      raise SolpsisInternalError('Error: unknown field name: '+ name)
    """
    return msg
  
  def createHeartbeatMsg(self):
    """Create a  HEARTBEAT message. Used to notify peers that we are still alive
    Headers: 'Id'    
    """
    msg = Message()
    msg.setMethod('HEARTBEAT')
    msg.addHeader('Id', self.node.getId())
    return msg

  def createDetectMsg(self, peer):
    """Create a DETECT message. Used to notify a neighbour that we have detected
    a peer moving toward this neighbour.
    Send info about this peer.
    Headers: 'Remote-Address', 'Remote-Id', 'Remote-Position',
    'Remote-AwarnessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
    """ 
    msg = Message()
    msg.setMethod('DETECT')
    self._addRemoteEntityInfosHeaders(msg, peer)
    return msg

  def createFoundMsg(self, peer):
    """ Create a FOUND message. This is the reply to a SEARCH message. We found a
    peer that could satisfy the SEARCH criteria. Send information on this remote
    peer.
    Headers: 'Remote-Address', 'Remote-Id', 'Remote-Position',
    'Remote-AwarnessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
    """ 
    msg = Message()
    msg.setMethod('FOUND')
    self._addRemoteEntityInfosHeaders(msg, peer)
    return msg

  def createSearchMsg(self, isClockwise):
    """ Create a SEARCH message. We need to search a new neighbour because our
    global connectivity rule isn't respected.
    isClockwise : if true search in clockwise direction
    Headers: 'Id', 'Clockwise'
    """
    msg = Message()
    msg.setMethod('SEARCH')
    msg.addHeader('Id', self.node.getId())
    msg.addHeader('Clockwise', isCounterclockwise)
    return msg
  
  def createQueryaroundMsg(self, idBest, distBest):
    """ Create a QUERYAROUND message. We around looking for all the peers that are
    located around a target position.
    idBest: Id of the peer that is the closest to target position
    distBest: distance of the best peer to target position
    Headers: 'Position', 'Best-Id', Best-Distance'
    """
    msg = Message()
    msg.setMethod('QUERYAROUND')
    msg.addHeader('Position', self.node.getStringPosition())
    msg.addHeader('Best-Id', idBest)
    msg.addHeader('Best-Distance',str(distBest))
    return msg

  def createNearestMsg(self, peer):
    """ Create a NEAREST message
    This is the reply to a FINDNEAREST message. Send information on the peer that
    is the nearest to a target position.
    Headers: 'Remote-Address', 'Remote-Position'
    """
    msg = Message()
    msg.setMethod('NEAREST')
    msg.addHeader('Remote-Address', peer.getAddress())
    msg.addHeader('Remote-Position', peer.getStringPosition())
    return msg

  def createAroundMsg(self, peer):
    """ Create a AROUND message. This the reply to a QUERYAROUND message.
    Send information on a peer that is around a target position.
    Headers: 'Remote-Address', 'Remote-Id', 'Remote-Position',
    'Remote-AwarnessRadius', 'Remote-Calibre', 'Remote-Orientation', 'Remote-Pseudo'
    """
    msg = Message()
    msg.setMethod('AROUND')
    self._addRemoteEntityInfosHeaders(msg, peer)
    return msg
  
class Message:
  VERSION = "SOLIPSIS/1.0"

  ALL_NODE_HEADERS = ['Address', 'Id', 'Position', 'AwarnessRadius', 'Calibre',
               'Orientation', 'Pseudo']
  
  ALL_REMOTE_HEADERS = [  'Remote-Address', 'Remote-Id', 'Remote-Position',
                          'Remote-AwarnessRadius', 'Remote-Calibre',
                          'Remote-Orientation', 'Remote-Pseudo']
  
  METHODS = {
    'AROUND'     : ALL_REMOTE_HEADERS,
    'BEST'       : ALL_NODE_HEADERS,
    'CLOSE'      : ['Id'],
    'CONNECT'    : ALL_NODE_HEADERS,
    'DETECT'     : ALL_REMOTE_HEADERS,
    'ENDSERVICE' : ['Id', 'ServiceId'],
    'FINDNEAREST': ['Position'],
    'FOUND'      : ALL_REMOTE_HEADERS,
    'HEARTBEAT'  : ['Id'],
    'HELLO'      : ALL_NODE_HEADERS,
    'NEAREST'    : ['Remote-Address', 'Remote-Position'],      
    'QUERYAROUND': ['Position', 'Best-Id', 'Best-Distance'],
    'SEARCH'     : ['Id', 'Clockwise'],
    'SERVICE'    : ['Id', 'ServiceId', 'ServiceDesc', 'ServiceAddress'],
    'UPDATE'     : ALL_NODE_HEADERS    
    }
  
  HEADERS_SYNTAX = {    
    'Address'       :  '\s*.*:\d+\s*',
    'AwarnessRadius': '\d+',
    'Calibre'       : '\d{1,4}',
    'Distance'      : '\d+',
    'Id'            : '.*',
    'Orientation'   : '\d{1,3}',
    'Position'      : '^\s*\d+\s*-\s*\d+$',
    'Pseudo'        : '.*'
    }
  HEADERS_SYNTAX['Best-Id']               = HEADERS_SYNTAX['Id']
  HEADERS_SYNTAX['Best-Distance']         = HEADERS_SYNTAX['Distance']
  HEADERS_SYNTAX['Remote-Address']        = HEADERS_SYNTAX['Address']
  HEADERS_SYNTAX['Remote-AwarnessRadius'] = HEADERS_SYNTAX['AwarnessRadius']
  HEADERS_SYNTAX['Remote-Calibre']        = HEADERS_SYNTAX['Calibre']
  HEADERS_SYNTAX['Remote-Distance']       = HEADERS_SYNTAX['Distance']
  HEADERS_SYNTAX['Remote-Id']             = HEADERS_SYNTAX['Id']
  HEADERS_SYNTAX['Remote-Orientation']    = HEADERS_SYNTAX['Orientation']
  HEADERS_SYNTAX['Remote-Position']       = HEADERS_SYNTAX['Position']
  HEADERS_SYNTAX['Remote-Pseudo']         = HEADERS_SYNTAX['Pseudo']
  
  def __init__(self, rawData=""):
    
    self.method = ""
    self.headers = []

    # create an empty message
    if rawData == "":
      self._data = ""      
    else:
      self._data = rawData
      # parse raw data to construct message
      data = rawData.splitlines()
      requestLinePattern = re.compile('(\w+)\s+(SOLIPSIS/\d+\.\d+)')
      requestLineMatch = requestLinePattern.match(data[0])
      if requestLineMatch is None:
        raise SolipsisMessageParsingError("Invalid message syntax")

      # Method is first word of the first line (e.g. NEAREST, or BEST ...)
      method = requestLineMatch.group(1).upper()
      # extract protocol version
      version = requestLineMatch.group(2).upper()
      
      if not Message.METHODS.has_key(method):        
        raise SolipsisMessageParsingError("Unknown method:" + method)

      self.method = method
      
      # Get headers for this method
      headerList = Message.METHODS[method]

      # We are looking for
      # * a word that can contain a '-' like Address or Remote-Address:
      #   (\w+(?:-\w+)?)  --> (?:) is used for non capturing groups, because we
      #                       don't want to catch '-Address' as a group 
      # * followed by a ':' : \s*:\s*
      # * and followed by anything - the header value : (.*) 
      headerPattern = re.compile(r'(\w+(?:-\w+)?)\s*:\s*(.*)')

      # Parse all headers included in message and check their syntax
      for line in data[1:]:        
        headerMatch = headerPattern.match(line)
        if headerMatch is None:
          raise SolipsisMessageParsingError("Invalid message syntax")

        # Get header name and header value
        headerName = headerMatch.group(1)
        headerVal = headerMatch.group(2)

        if headerName not in headerList:
          raise SolipsisMessageParsingError("Unknown header " + headerName +
                                            " for message " + method)
        
        
        # check the syntax of the header (e.g. for a calibre we expect a 3 digits
        # number)
        if Message.HEADERS_SYNTAX.has_key(headerName):
          # syntax of each header is stored in HEADERS_SYNTAX hash table
          headerSyntax = re.compile(Message.HEADERS_SYNTAX[headerName])
          if headerSyntax.match(headerVal) is not None:
            # the syntax is correct add this header to the Message object
            self.addHeader(headerName, headerVal)
          else:
            raise SolipsisMessageParsingError("Invalid header '" + headerName +
                                              "' syntax:" + headerVal)          
        else:
          # we have an unknown header, if solipsis version is different just
          # skip this header, else raise an error
          if version == VERSION:
            raise SolipsisMessageParsingError(Message.VERSION + "Unknown header " +
                                              headerName + " in message " + method)

      # We have added all the headers we need to check now 
      # that all headers where added to the message
      if len(self.headers) < len(headerList):
        # some headers are missing
        raise SolipsisMessageParsingError("Missing headers in message " + method)
      elif len(self.headers) > len(headerList):
        # we have added too many headers, it means that we have duplicate headers
        raise SolipsisMessageParsingError("Duplicate header in message "+ method)
      
  def addHeader(self, header, value):
    self.headers[header] = value

  def setMethod(self, value):
    self.method = value
    
  def data(self):
    buffer = self.method + " " + Message.VERSION + "\r\n"
    for (k,v) in self.headers.items():
      line =  '%s: %s\r\n' % (k, str(v))
      buffer = buffer + line
    return buffer
    
  def __repr__(self):
    """ String representation of the message """
    return self.data()

