#!/usr/bin/python
# Copyright (c) 2003 CORE Security Technologies
#
# This software is provided under under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# $Id: sniffer.py,v 1.3 2003/10/27 17:36:56 jkohen Exp $
#
# Simple packet sniffer.
#
# This packet sniffer uses a raw socket to listen for packets
# in transit corresponding to the specified protocols.
#
# Note that the user might need special permissions to be able to use
# raw sockets.
#
# Authors:
#  Gerardo Richarte <gera@coresecurity.com>
#  Javier Kohen <jkohen@coresecurity.com>
#
# Reference for:
#  ImpactDecoder.

from select import select
import socket
import sys

import impacket
from impacket import ImpactDecoder

DEFAULT_PROTOCOLS = ('tcp',)

def sniff(punch):
    toListen = DEFAULT_PROTOCOLS
        
    # Open one socket for each specified protocol.
    # A special option is set on the socket so that IP headers are included with
    # the returned data.
    sockets = []
    for protocol in toListen:
	try:
            protocol_num = socket.getprotobyname(protocol)
	except socket.error:
            print "Ignoring unknown protocol:", protocol
            toListen.remove(protocol)
            continue
	s = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol_num)
	s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
	sockets.append(s)

    if 0 == len(toListen):
	print "There are no protocols available."
	sys.exit(0)

    print "Listening on protocols:", toListen

    # Instantiate an IP packets decoder.
    # As all the packets include their IP header, that decoder only is enough.
    decoder = ImpactDecoder.IPDecoder()
    captured = 0
    while len(sockets) > 0 and not captured:
	# Wait for an incoming packet on any socket.
        print 'wait'
	ready = select(sockets, [], [])[0]
	for s in ready:
            packet = s.recvfrom(4096)[0]
            if 0 == len(packet):
                # Socket remotely closed. Discard it.
                sockets.remove(s)
                s.close()
            else:
                # Packet received. Decode and display it.
                packet = decoder.decode(packet)
                value = {}
                try:
                    value['timestamp']=timestamp
                    value['shost']=packet.child().get_ip_src()
                    value['dhost']=packet.child().get_ip_dst()
                    value['proto']=packet.child().child().protocol
                    value['sport']=-1
                    value['dport']=-1
                except:
                    return
                
                try:
                    if value['proto'] == socket.IPPROTO_TCP:
                        value['dport']=packet.child().child().get_th_dport()
                        value['sport']=packet.child().child().get_th_sport()
                except:
                    pass
                
                if value['dhost'] == punch.remotePublicAddress[0] and \
                       value['dport'] == punch.remotePublicAddress[1] and \
                       value['shost'] == punch.privateAddress[0] and \
                       value['sport'] == punch.privateAddress[1]:
                    
                    print packet.get_ip_dst()
                    print packet.child().get_th_dport()
                    captured = 1
                else:
                    print packet
                    captured = 1
                    
