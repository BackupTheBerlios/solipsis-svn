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
## -----                           Media.py                                   -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module allows the initialization of a new Navigator/Media modules.
##   It defines the class Media
##   A Navigator owns several Services
##
## ******************************************************************************

class Media:
  
  def __init__(self, id, host, port, emissive_object, pushOrPull):
    """ All informations about media:
    host --> ip,
    port --> integer, 
    emissive_object --> the thread for message exchange,
    pushOrPull --> 1 if every modification should be sent, 0 else"""

    # media identifier
    self.id = id

    # media host and port
    self.host = host
    self.port = int(port)

    # thread for communication
    self.thread = emissive_object

    # push = 1 --> every modif should be sent
    self.push = pushOrPull

    # media services
    # {id_service: [desc_service, host, port]
    self.services = {}

    # recensed bug in transmission
    self.bug = 0

  def addBug(self):
    """ a bug is raised during a transmission
    if 3 bugs, return 1"""

    self.bug += 1

    if self.bug == 3:
#      return 1 # some not fixed bugs
      return 0

    return 0

