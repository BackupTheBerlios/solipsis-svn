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

import ConfigParser, logging, logging.config

# Solipsis Packages
from solipsis.util.parameter import Parameters
from solipsis.engine.node import Node

#################################################################################################
#                                                                                               #
#				     -------  main ---------				        #
#                                                                                               #
#################################################################################################

#-----Step 0: Initialize my informations

def main():
  try:
    configFileName = "conf/solipsis.conf"
    params = Parameters(configFileName)
    
    myNode = Node(params)
    myNode.mainLoop()
  except:
    raise

if __name__ == '__main__':
    main()



