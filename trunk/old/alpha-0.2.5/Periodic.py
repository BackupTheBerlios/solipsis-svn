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
## -----                           Periodic.py                              -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module defines a generic class for any task that is runned on a
##   periodic basis.
##   Then, it gives the functions that are required for the definition of these
##   periodic tasks :
##   - Heartbeat : node sends heartbeat messages to its neighbors
##   - Global Connectivity : nodes should verify on a regular basis that it
##   still respects the Global Connectivity rule
##   - fileManagement : this class allow the node to update the file for the
##   future connection
##   - modifAR : on a regular basis, the node adjusts its awareness radius
##   - adjacent policy : this regular task manage the set of neighbors of the
##   entity
##
## ******************************************************************************

from threading import Thread
from socket import gethostbyname
import string
import random
import time

from Function import *
import globalvars

#################################################################################################
#                                                                                               #
#			----- generic thread for regular check ---------			#
#                                                                                               #
#################################################################################################

class GenericThread(Thread):

  def __init__(self, fct, temp, stopCond, addData = 0):
    Thread.__init__(self)

    # fct is the descriptor of the function to be called periodically
    self.fct = fct

    # addData is a class containing personal data used by the function
    self.data = addData

    # stopCond is the descriptor of the function tested for the stop condition
    self.stop = stopCond

    # temp is the period in seconds
    self.temp = temp

  def run(self):

    while eval(self.stop)():

      time.sleep(self.temp)
      
      globalvars.mutex.acquire()
      eval(self.fct)(self.data)
      globalvars.mutex.release()

    print "End of periodic thread %s \n" % self.fct

#################################################################################################
#                                                                                               #
#			----- data for management of heartbeat messages ---------		#
#                                                                                               #
#################################################################################################

class HeartbeatData:
  """ class of data for the management of heartbeat messages"""

  def __init__(self):

    # list of entities that are suspected to be dead
    self.suspect = []
    
#################################################
#              HeartbeatFunction                #
#################################################

def heartbeatFunction(data):
  """ function for heartbeat management"""

  # time stamp
  time_stamp = time.time()

  for ent in globalvars.me.adjacents.values():

    if not ent.message_received:

      # no message received since last time
      if ent in data.suspect:
        # this entity seems to be dead
        data.suspect.remove(ent)
        closeConnection(ent)

      else:
        # add ent to list of suspect
        data.suspect.append(ent)

    if not ent.message_sent:
      # send Heartbeat messages
      try:
        ent.sendNetworkMessage(encodeMsg(["HEARTBEAT", str(globalvars.me.ident)]))
      except:
        pass

    # re-init variable
    ent.message_received = 0
    ent.message_sent = 0

#################################################################################################
#                                                                                               #
#			----- data for management of global connectivity ---------		#
#                                                                                               #
#################################################################################################

def globalConnectivityFunction(data):
  """ check the global connectivity"""

  if not len(globalvars.me.adjacents):
    # connexion algoprithm
    globalvars.me.worldEntrance()

  else:
    # check globalconnectivity
    bad_entities = globalvars.me.ccwAdjacents.checkGlobalConnectivity()
    for pair in bad_entities:
      # send message to each entity
      list1 = ["SEARCH", globalvars.me.ident, "1"]
      list2 = ["SEARCH", globalvars.me.ident, "0"]
      msg1 = encodeMsg(list1)
      msg2 = encodeMsg(list2)
      
      pair[0].sendNetworkMessage(msg1)
      pair[1].sendNetworkMessage(msg2)

#################################################################################################
#                                                                                               #
#			----- data for entities.met management ---------         		#
#                                                                                               #
#################################################################################################

def fileManagementFunction(data):
    """ informations on met entities are saved
    in the file 'entities.met' for further
    world connection"""

    if random.random() > 0.01:
      return

    #------- step 1 : read informations and add new info

    # retrieve_data = {(hostname, port) : 1..}
    retrieve_data = {}

    # open file
    try:
      f = file('entities.met', 'r')
    except:
      return

    # read all file
    for line in f:
        try:
            host, port = line.split()

            # put the data in a dictionary
            retrieve_data[(host, port)] = 1
        except:
            pass

    f.close()

    # add new informations to file informations
    for (host, port) in globalvars.me.met.keys():
            retrieve_data[(host, port)] = 1

    #-------- step 2 : choose 1000 entities

    # change dictionary entry in list
    list_retrieve = retrieve_data.keys()
    length = len(list_retrieve)

    if length > 1000:
    
      # random choice of 1000 entities
      pre = random.randint(0, length)
      if pre + 1000 > length:
        list_met = list_retrieve[pre:]
        remain = 1000 - (length - pre)
        list_met.extend(list_retrieve[:remain])
      else:
        list_met = list_retrieve[pre:(pre+1000)]
    
    else:
      # the whole list of entities is written in file
      list_met = list_retrieve

    # -------- step 3 : put informations in the file
    
    f = file('entities.met', 'w')
    
    # put in the file
    for (host, port) in list_met:
      entry = host + " " + str(port) + "\n"
      f.write(entry)

    f.close()

    # update informations on met entities
    globalvars.me.met.clear()
    globalvars.me.nb_met = 0

#################################################################################################
#                                                                                               #
#			----- data for adjacent policy and AR management ---------		#
#                                                                                               #
#################################################################################################

class AdjacentData:

  def __init__(self):

    # ratio between number of adjacents and adjacents in Awareness Radius
    self.ratio_ar = 1.5
    
    # maximal ratio between number of adjacents in AR and expected number
    self.ratio_increase = 1.25
    
    # minimal ratio between number of adjacents in AR and expected number
    self.ratio_decrease = 0.75

    # coef for modification of Awareness Radius
    self.modif_ar = 0.25
    
    # last modification of Awareness Radius
    self.last_modif = 0

#################################################
#              modifAR                          #
#################################################

def modifAr(aw, sense, data):
    """ Awareness radius aw need to be changed in the sense 0 if it should diminish
    and 1 if it should grow
    return the value of the modification"""

    if not data.last_modif:

      # it is the first change of Awareness radius
      if sense:
        result = data.modif_ar * aw
      
      else:
        result = - (data.modif_ar * aw)

    else:

      if sense == (data.last_modif < 0):
        # the sense is different that last time
        # modification by an upper value than last time
        result =  - (data.last_modif * (1 - data.modif_ar))

      else:
        # same sense that last time
        # modification by an under value than last time
        result = data.last_modif * (1 + data.modif_ar)

    # update last_modif
    data.last_modif = result
    
    return long(result)
  
#################################################
#              AdjacentFunction                 #
#################################################

def adjacentFunction(data):

  if globalvars.me.connected:

    # count the number of entities inside AR
    number_of_entity_in_ar = globalvars.me.distAdjacents.closer_to_d(globalvars.me.awareness_radius)

    #----- Close connection if too many neighbors outside Awareness Radius

    if ( len(globalvars.me.adjacents) > data.ratio_ar * number_of_entity_in_ar ) and ( len(globalvars.me.adjacents) > globalvars.me.exp ):

      # choose entity to remove
      closedEntity = chooseForRemove()

      if closedEntity <> 0:
        # close chosen entity
        try:
          closedEntity.sendNetworkMessage(encodeMsg(["CLOSE", globalvars.me.ident]))
          closeConnection(closedEntity)
        except:
          pass

    #----- Update the Awareness Radius.

    # if too many neighbours in Awareness Area, decrease Awareness Area
    if (data.ratio_increase * globalvars.me.exp) < number_of_entity_in_ar and globalvars.me.awareness_radius > 1:
      varAR = modifAr(globalvars.me.awareness_radius, 0, data)
      globalvars.me.updateAR(varAR)

      # if too few neighbours in Awareness Area, increase Awareness Area
    elif (data.ratio_decrease * globalvars.me.exp) > number_of_entity_in_ar and globalvars.me.awareness_radius < globalvars.SIZE:
      varAR = modifAr(globalvars.me.awareness_radius, 1, data)
      globalvars.me.updateAR(varAR)

#################################################################################################
#                                                                                               #
#			----- data for notification of aliveness to a server ---------		#
#                                                                                               #
#################################################################################################

class StatData:

  def __init__(self, host, port):

    # variable incremented by one at each iteration
    self.counter = 0

    # every period iterations, a message is sent
    self.period = 100

    # server address
    self.server_host = host
    self.server_port = port

def statSender(data):
  """ send a notification of aliveness and position every 'period'"""
  
  if not (data.counter % data.period):
    message = globalvars.me.ident + " " + str(globalvars.me.position[0]) + " " + str(globalvars.me.position[1])
    try:
      globalvars.me.socket.sendto( message, (data.server_host, data.server_port) )
    except:
      pass

    data.counter = 0

  data.counter += 1
