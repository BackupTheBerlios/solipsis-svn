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
## -----                           service.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the service interface.
##   It is the parent class of all the services available in the application.
##
## ******************************************************************************

import socket
from threading import Thread

class Service(Thread):

    def __init__(self, id_service, desc_service, host, port):
        Thread.__init__(self)

        # name of service
        self.id_service = id_service

        # communication
        self.my_host = host
        self.my_port_service = port

        # create UDP connection for services modules
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while 1:
            try:
                self.udp_socket.bind((self.my_host, self.my_port_service))
                break
            except:
                # may be the port is already used
                time.sleep(0.2)
                self.my_port_service = random.randint(1000,25000)

        # list of neighbors owning similar service
        # {id:[object_neighbor]}
        self.list_neighbors = {}

        # in order to kill the thread
        self.alive = 1

    # ---------------------------------

    def insert_service(self, node, host, port):
        """ insert the node in the list_neighbor """

        raise "error"


    def delete_service(self, node):
        """ remove the node from the list_neighbor """


        raise "error"



    def update(self, node, delta_x, delta_y):

        raise "error"


    def run(self):

        raise "error"

    def close(self):
        """ close the service """
        #print "service.close()"

        # kill the thread
        self.alive = 0

        # close UDP connection for chat module
        self.udp_socket.close()

        # empty the list of neighbors
        self.list_neighbors = {}
