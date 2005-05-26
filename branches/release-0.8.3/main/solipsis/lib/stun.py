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

# This code comes from Shtoom: http://www.divmod.org/Home/Projects/Shtoom/
# Licensed under the GNU LGPL.
# Copyright (C) 2004 Anthony Baxter
# $Id$

import struct, socket, time, logging

from twisted.internet import reactor, defer
from twisted.internet.protocol import DatagramProtocol


# This should be replaced with lookups of
# _stun._udp.divmod.com and _stun._udp.wirlab.net
DefaultServers = [
    ('stun.xten.net', 3478),
    ('sip.iptel.org', 3478),
    ('stun2.wirlab.net', 3478),
    ('stun.wirlab.net', 3478),
    ('stun1.vovida.org', 3478),
    ('tesla.divmod.net', 3478),
    ('erlang.divmod.net', 3478),
]

StunTypes = {
   0x0001: 'MAPPED-ADDRESS',
   0x0002: 'RESPONSE-ADDRESS ',
   0x0003: 'CHANGE-REQUEST',
   0x0004: 'SOURCE-ADDRESS',
   0x0005: 'CHANGED-ADDRESS',
   0x0006: 'USERNAME',
   0x0007: 'PASSWORD',
   0x0008: 'MESSAGE-INTEGRITY',
   0x0009: 'ERROR-CODE',
   0x000a: 'UNKNOWN-ATTRIBUTES',
   0x000b: 'REFLECTED-FROM',
}

import os
if os.path.exists('/dev/urandom'):
    def getRandomTID():
        return open('/dev/urandom').read(16)
else:
    def getRandomTID():
        # It's not necessary to have a particularly strong TID here
        import random
        tid = [ chr(random.randint(0,255)) for x in range(16) ]
        tid = ''.join(tid)
        return tid

class StunProtocol(DatagramProtocol, object):
    def __init__(self, servers=DefaultServers, *args, **kwargs):
        self._pending = {}
        self.servers = servers
        super(StunProtocol, self).__init__(*args, **kwargs)

    def datagramReceived(self, dgram, address):
        mt, pktlen, tid = struct.unpack('!hh16s', dgram[:20])
        # Check tid is one we sent and haven't had a reply to yet
        if self._pending.has_key(tid):
            del self._pending[tid]
        else:
            logging.error("error, unknown transaction ID %s, have %r" % (tid, self._pending.keys()))
            return
        if mt == 0x0101:
            logging.info("got STUN response from %s"%repr(address))
            # response
            remainder = dgram[20:]
            while remainder:
                avtype, avlen = struct.unpack('!hh', remainder[:4])
                val = remainder[4:4+avlen]
                avtype = StunTypes.get(avtype, '(Unknown type %04x)'%avtype)
                remainder = remainder[4+avlen:]
                if avtype in ('MAPPED-ADDRESS',
                              'CHANGED-ADDRESS',
                              'SOURCE-ADDRESS'):
                    dummy,family,port,addr = struct.unpack('!ccH4s', val)
                    if avtype == 'MAPPED-ADDRESS':
                        self.gotMappedAddress(socket.inet_ntoa(addr),port)
                else:
                    logging.info("STUN: unhandled AV %s, val %r" % (avtype, repr(val)))
        elif mt == 0x0111:
            logging.error("STUN got an error response")

    def gotMappedAddress(self, addr, port):
        logging.info("got address %s %s (should I have been overridden?)" % (addr, port))

    def sendRequest(self, server, avpairs=()):
        tid = getRandomTID()
        mt = 0x1 # binding request
        avstr = ''
        # add any attributes
        for a,v in avpairs:
            raise NotImplementedError, "implement avpairs"
        pktlen = len(avstr)
        if pktlen > 65535:
            raise ValueError, "stun request too big (%d bytes)"%pktlen
        pkt = struct.pack('!hh16s', mt, pktlen, tid) + avstr
        self._pending[tid] = (time.time(), server)
        # install a callLater for retransmit and timeouts
        self.transport.write(pkt, server)

    def blatServers(self):
        for s in self.servers:
#             print "sending to", s
            self.sendRequest(s)
