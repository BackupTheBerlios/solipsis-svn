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
## -----                           Node.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the main module of SOLIPSIS.
##   It initializes the node and launches all threads.
##   It involves the bootstrap and the message for network address retrieval
##
## ******************************************************************************

from socket import socket, AF_INET, SOCK_DGRAM, gethostbyname
import sys, random, string
from threading import Lock, Thread, Timer
import time

# Solipsis Packages
import Periodic
import Self
import Network
import GUI
import Entity
import globalvars
from Function import *

#################################################################################################
#                                                                                               #
#	               -------  Thread for reception of Hi messages ---------		        #
#                                                                                               #
#################################################################################################

class HiReception(Thread):
  
  def __init__(self, sock):
    Thread.__init__(self)
    self.socket = sock

    self.cont = 1

  def run(self):
    """ Receive messages from other nodes and process them"""

    global found, host, port, ent_host, ent_port
    
    while self.cont:

      time.sleep(0.2)

      try:
        # receive and process message from other nodes
        data, add = self.socket.recvfrom(2000)

        # retrieve data 
        host, port, ent_host, ent_port = data.split(";")

        # update global variable found
        found = 1

      except:
        pass

    print('Connection Algorithm...\n')

  def stop(self):
    """ receive instruction to stop the thread"""

    self.cont = 0

#################################################################################################
#                                                                                               #
#				     -------  main ---------				        #
#                                                                                               #
#################################################################################################

#-----Step 0: Initialize my informations

# default values
tcp_port = random.randint(1024, int(2**16))
posX = long(random.random() * globalvars.SIZE)
posY = long(random.random() * globalvars.SIZE)
ar = 1
ca = 1024
ori = 0 
exp = 12
pseudo = "anonymous_"+str(tcp_port)

# optional argument
statInfos = 1
i = 1
length = len(sys.argv) - 1


try:

  if length == 1:
    raise error
  
  while i < length and length > 0:

    # retrieve argument
    option = sys.argv[i]

    # check if this argument is an option
    if option[0] == "-":

      # retrieve the option
      changed_option = option[1]

      # option has interest only if there is an argument behind
      if i+1 <= length:
        
        # option is tcp_port
        if changed_option == "t":
          tcp_port = int(sys.argv[i+1])
          if not (0 < tcp_port < 2**16):
            raise error

        # option is pos x
        if changed_option == "x":
          posX = long(sys.argv[i+1]) % globalvars.SIZE

        # option is pos y
        if changed_option == "y":
          posY = long(sys.argv[i+1]) % globalvars.SIZE

        # option is caliber
        if changed_option == "c":
          caliber = int(sys.argv[i+1])
          if not (0 < caliber < 1024):
            raise error

        # option is the expected number of adjacents
        if changed_option == "e":
          exp = int(sys.argv[i+1])
          if not (0 < exp):
            raise error

        # option is pseudo
        if changed_option == "n":
          pseudo = sys.argv[i+1]

        # no notification to server
        if changed_option == "z":
          statInfos = 0
          i -= 1

      i += 2
      
    else:
      
      i += 1
                      
except:
  sys.stderr.write("\nOptions :\n")
  sys.stderr.write("    -t : change tcp port for interface module <-> node\n")
  sys.stderr.write("    -x : change position x\n")
  sys.stderr.write("    -y : change position y\n")
  sys.stderr.write("    -c : change caliber\n")
  sys.stderr.write("    -e : change expected number of neighbors\n")
  sys.stderr.write("    -n : change pseudo\n")
  sys.exit(0)


########################################################################
#-----Step 0 bis: retrieve our IP host ! **** NAT issue
########################################################################

# create a temporary socket
s = socket(AF_INET, SOCK_DGRAM)
s.setblocking(0)

# create thread for message reception
receive_hi = HiReception(s)
receive_hi.start()

# open file 'entities.met'
try:
  f = file('entities.met', 'r')
except:
  sys.stderr.write("No file for connection...")
  receive_hi.stop()
  sys.exit(0)

# read file and close
list = f.readlines()
f.close()

# create message "HI"
message = "HI"

# init while
time_stamp = time.time()
found = 0

while not found:

  # retrieve entity
  entity = random.choice(list)
  host, stringPort = entity.split()
  port = int(stringPort)
  
  # send message
  s.sendto(message, (host, port) )
  
  time.sleep(0.2)
  if time.time() > time_stamp + 30.:
    receive_hi.stop()
    break

if not found:
  
  s.close()
  sys.stderr.write('The connection to Solipsis world failed\n')
  sys.stderr.write('Please download a new bootstrap file...\n')

else:

  # put host in file
  f = file(str(pseudo)+".host", 'w')
  f.write(host)
  f.close()
  
  # close thread for reception of "HI" message
  receive_hi.stop()
  time.sleep(0.25)

  # switch the socket to blocking mode
  s.setblocking(1)

  ########################################################################
  #-----Step 1 : launch node
  ########################################################################
  
  # creation of my node
  globalvars.me = Self.Self_Infos(host, port, s, tcp_port, posX, posY, ar, ca, ori, exp, pseudo)
  #f2 = file("mytest.txt", 'w')
  #f2.write("lmlm")
  #f2.close()

  # connection
  globalvars.ALIVE = 1
  globalvars.me.worldEntrance(ent_host, ent_port)

  ########################################################################
  #-----Step 2: run thread for message reception
  ########################################################################
  
  NtThread = Network.Network_Reception()
  NtThread.start()
  
  ########################################################################
  #-----Step 3: run thread for GUI method invokation
  ########################################################################
  
  GUIThread = GUI.GUI(globalvars.me.host, globalvars.me.GUI_port, GUI.GUI_Functions())
  GUIThread.start()

  ########################################################################
  #-----Step 4: run several threads for periodic tasks
  ########################################################################
  
  # thread for heartbeat messages
  heartbeat_data = Periodic.HeartbeatData()
  heartbeat = Periodic.GenericThread("heartbeatFunction", 10., "isAlive", heartbeat_data)
  heartbeat.start()

  # thread for global connectivity checks
  global_connectivity = Periodic.GenericThread("globalConnectivityFunction", 8., "isAlive")
  global_connectivity.start()

  # thread for adjacent policy and awareness radius management
  adjacent_data = Periodic.AdjacentData()
  adjacent = Periodic.GenericThread("adjacentFunction", 1.5, "isAlive", adjacent_data)
  adjacent.start()

  # thread for file entities.met management
  file_management = Periodic.GenericThread("fileManagementFunction", 6., "isAlive")
  file_management.start()

  if statInfos:
    # Thread that notifies the position and the aliveness of the entity
    # to a server.
    # The server does not keep entity id for any other use than
    # counting the number of alive entities
    # paranoid users are invited to use option -z to skip this thread

    try:
      # address of the server
      server_host = gethostbyname("stats.netofpeers.net")
      server_port = 22675
      stat_data = Periodic.StatData(server_host, server_port)

      # first notification
      Periodic.statSender(stat_data)

      # periodic notifications
      stat_sender = Periodic.GenericThread("statSender", 6., "isAlive", stat_data)
      stat_sender.start()
    except:
      pass

