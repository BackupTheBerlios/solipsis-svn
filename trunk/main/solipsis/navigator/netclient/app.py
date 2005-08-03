# pylint: disable-msg=C0103
# Invalid name
# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>
"""Specific class for net application: navigator without wx"""

import gettext
import threading
import sys
_ = gettext.gettext

from solipsis.services.collector import ServiceCollector
from solipsis.node.discovery.stun import DiscoverAddress

from solipsis.navigator.app import BaseNavigatorApp
from solipsis.navigator.world import BaseWorld
from solipsis.navigator.netclient.viewport import Viewport
from solipsis.navigator.netclient.network import NetworkLoop, SolipsisUiFactory
from solipsis.navigator.netclient.config import ConfigData

class NavigatorApp(BaseNavigatorApp):
    """specific class to launch a simple non-graphic navigator"""

    def __init__(self, params, *args, **kargs):
        """available kargs: port"""
        BaseNavigatorApp.__init__(self, params, *args, **kargs)
        self.config_data = ConfigData(self.params)
        self.listener = None
        self.OnInit()
        
    def OnInit(self):
        """
        Main initialization handler.
        """
        BaseNavigatorApp.OnInit(self)
        self.InitTwisted()
        self.InitNetwork()

    def InitIpAddress(self):
        """
        Get local address from Stun
        """
        def _succeed(address):
            """Discovery succeeded"""
            self.local_ip, port = address
            print "discovery found address %s:%d" % (self.local_ip, port)
            self.InitServices()
        def _fail(failure):
            """Discovery failed => try next discovery method"""
            print "discovery failed:", failure.getErrorMessage()
            print 'using getHostByName:', self.local_ip
            self.InitServices()
        deferred = DiscoverAddress(self.params.port, self.reactor, self.params)
        deferred.addCallback(_succeed)
        deferred.addErrback(_fail)
        return deferred

    def InitResources(self):
        """Create world"""
        self.viewport = Viewport()
        self.world = BaseWorld(self.viewport)

    def InitNetwork(self):
        """
        Launch network event loop.
        """
        self.network_loop = NetworkLoop(self.reactor, self)
        self.listener = self.reactor.listenTCP(self.local_port,
                                               SolipsisUiFactory(self))
        print "listening on port", self.local_port
        BaseNavigatorApp.InitNetwork(self)

    def InitServices(self):
        """
        Initialize all services.
        """
        assert self.config_data, "config must be initialised first"
        self.services = ServiceCollector(self.params, self.local_ip,
                                         self.reactor, self)
        if self.config_data.used_services:
            for service in self.config_data.used_services:
                service_path = self.services._ServiceDirectory(service)
                service_id, plugin = self.services.LoadService(service_path,
                                                               service)
                self.services.InitService(service_id, plugin)
                self.services.SetNode(self.config_data.GetNode())
                self.services.EnableServices()
                self.config_data.SetServices(self.services.GetServices())
        else:
            BaseNavigatorApp.InitServices(self)

    def stopListening(self):
        """close connection from manager and stop accepting"""
        if self.listener:
            defered = self.listener.stopListening()
            self.listener = None
            return defered
        else:
            return None

    #
    # Helpers
    #
    def future_call(self, delay, function):
        """call function after delay (milli sec)"""
        threading.Timer(delay/1000, function).start()

    def display_message(self, title, msg):
        """Display message to user, using for instance a dialog"""
        print title, ":", msg

    def display_error(self, title, msg):
        """Report error to user"""
        print >> sys.stderr, title, ":", msg

    def display_status(self, msg):
        """report a status"""
        print msg

    def _DestroyProgress(self):
        """
        Destroy progress dialog if necessary.
        """
        pass
    
    def _SetWaiting(self, waiting):
        """
        Set "waiting" state of the interface.
        """
        pass


        

