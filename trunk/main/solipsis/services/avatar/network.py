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

import os

from twisted.web import resource, server, static



class NetworkLauncher(object):
    def __init__(self, reactor, plugin, port):
        self.reactor = reactor
        self.plugin = plugin
        self.port = port
        self.listening = None
        self.root_resource = resource.Resource()
        self.server_site = server.Site(self.root_resource)
        #~ self.SetFile('img/avat_gh.png')
        #~ self.SetFile('COPYRIGHT')

    def Start(self):
        if self.listening:
            self.Stop()
        self.listening = self.reactor.listenTCP(self.port, self.server_site)

    def Stop(self):
        if self.listening:
            self.listening.stopListening()
        self.listening = None

    def SetFile(self, filename):
        path = os.path.realpath(os.path.normcase(filename))
        resource = static.File(path)
        resource.isLeaf = 1
        self.root_resource.putChild('avatar', resource)
