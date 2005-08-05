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

import socket

import twisted.internet.defer as defer

import solipsis.lib.shtoom.nat as nat

local_timeout = 0.5

# def DiscoverAddress(port, reactor, params):
#     try:
#         host = socket.gethostbyname(socket.gethostname())
#     except Exception, e:
#         return defer.fail(e)
#     else:
#         return defer.succeed((host, port))

def DiscoverAddress(port, reactor, params):
    d = defer.Deferred()
    d_ip = nat.getLocalIPAddress()
    def _timeout():
        if not d.called:
            d.errback(Exception("timed out"))
    def _got_local_ip(ip):
        if not d.called:
            if ip:
                d.callback((ip, port))
            else:
                d.errback(Exception("no address found"))

    d_ip.addCallback(_got_local_ip).addErrback(d.errback)
    reactor.callLater(local_timeout, _timeout)
    return d

