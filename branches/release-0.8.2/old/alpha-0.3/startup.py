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
## -----                           startup.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the main module of SOLIPSIS.
##   It initializes the node and launches all threads.
##   It involves the bootstrap and the message for network address retrieval
##
## ******************************************************************************

#import random, string, time
#from threading import Lock, Thread, Timer
import ConfigParser, logging, logging.config
#from Queue import Queue

# Solipsis Packages
from parameter import Parameters
from node import Node

#################################################################################################
#                                                                                               #
#				     -------  main ---------				        #
#                                                                                               #
#################################################################################################

#-----Step 0: Initialize my informations

# default values
try:
  configFileName = "solipsis.conf"
  param = Parameters(configFileName)
  
  myNode = Node(param)
  myNode.mainLoop()
except:
  raise



