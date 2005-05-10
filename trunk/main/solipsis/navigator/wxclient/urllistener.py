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

import re

from twisted.internet import protocol
from twisted.protocols import basic

from solipsis.util.address import Address

class URLListenProtocol(basic.LineReceiver):
    def lineReceived(self, url):
        self.factory.ProcessURL(url)
        self.transport.loseConnection()

class URLListenFactory(protocol.ServerFactory):
    protocol = URLListenProtocol
    url_regexp = r'^slp://(\d+\.\d+\.\d+\.\d+):(\d+)/?$'

    def __init__(self, ui):
        self.ui = ui
        self.url_pattern = re.compile(self.url_regexp)

    def ProcessURL(self, url):
        self.ui._JumpNearURL(url)
