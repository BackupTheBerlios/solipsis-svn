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


import sys

from solipsis.core.node import Node
from solipsis.core.peerevent import PeerEvent
from solipsis.core.event import EventFactory
from solipsis.util.address import Address
import state

class StartingState(state.State):
    """ Additionnal state needed for the seeds"""
    def __init__(self):
        self.startTimer()
        self.portList = self.getPortList()

    def getPortList(self):
        """ Read seed.met file and return the list of port of all the seeds"""
        try:
            # read file and close
            name = 'conf/seed.met'
            f = file(name, 'r')
            lines = f.readlines()
            f.close()
        except:
            sys.stderr.write("Error - cannot read file:" + name)
            sys.exit(0)
        portList = []
        for line in lines:
                if line.strip() <> "":
                    port, x, y = line.split()
                    portList.append(int(port))
        return portList

    def TIMER(self, event):
        manager = self.node.getPeersManager()
        nbSeeds = len(self.portList)
        nbPeers = manager.getNumberOfPeers()
        # we have connected to all other seeds
        if nbPeers == nbSeeds -1 :
            self.logger.debug('Entering Idle state')
            ar = manager.computeAwarenessRadius()
            self.node.setAwarenessRadius(ar)
            self.node.setExpectedPeers(nbPeers)
            self.node.startPeriodicTasks()
            self.sendUpdate()
            self.node.setState(state.Idle())
        else:
            self.logger.debug('Not connected to all seeds: %d/%d', nbPeers,
                              nbSeeds -1)

            # relaunch timer
            self.startTimer()

            connectedPorts = []
            for peer in manager.enumeratePeers():
                connectedPorts.append(peer.getAddress().getPort())

            #self.logger.debug('ports: %s' , str(connectedPorts))

            for port in self.portList:
                if (port <> self.node.getAddress().getPort()) and \
                       ( port not in connectedPorts):
                    f = EventFactory.getInstance(PeerEvent.TYPE)
                    hello = f.createHELLO()
                    hello.setRecipientAddress(Address(self.node.host, port))
                    self.node.dispatch(hello)

class Seed(Node):

    def __init__(self, params):
        #params = self.modifyConf(params)
        # call parent class constructor
        super(Seed, self).__init__(params)

        self.setState(StartingState())
