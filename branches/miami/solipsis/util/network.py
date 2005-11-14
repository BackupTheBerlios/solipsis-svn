#<copyright>
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
"""Provides a few method for network management"""

import socket

FREE_PORTS = range(23000, 23999)

def parse_address(address):
    """Parse network address as supplied by a peer.
    Returns a (host, port) tuple."""
    try:
        items = address.split(':')
        if len(items) != 2:
            raise ValueError("address %s expected as host:port"% address)
        host = str(items[0]).strip()
        port = int(items[1])
        if not host:
            raise ValueError("no host in %s"% address)
        if port < 1 or port > 65535:
            raise ValueError("port %d should be in [1, 65535]"% port)
        return host, port
    except ValueError:
        raise ValueError("address %s not valid"% address)

def get_free_port():
    """return available port on localhost"""
    free_port = FREE_PORTS.pop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
    try:
        # connect to the given host:port
        sock.bind(("127.0.0.1", free_port))
    except socket.error:
        free_port = get_free_port()
    else:
        sock.close()
    return free_port

def release_port(port):
    """call when server stops listening"""
    FREE_PORTS.append(port)
