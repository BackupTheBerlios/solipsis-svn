# Echo server program
import struct, socket
import sys, time
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import threads
import twisted.internet.defer as defer

import signal, os
import random
from impacket import ImpactPacket


class Spoofy:
    """
    If a spoofing request is received, waits for the two SYN numbers
    and spoof the relative SYNACK packets
    """

    def __init__(self, punch):
        self.punch = punch
    
    
    def rcvForcingTcpRequest(self):
        value = {}
        value['srcAddress'] = self.punch.getAddress('REQUESTOR-PUBLIC-ADDRESSE')
        value['dstAddress'] = self.punch.getAddress('PUBLIC-ADDRESSE')
        value['SYN'] = struct.unpack('!L', self.punch.avtypeList['SYN'])[0]

        print 'Register Request', value['srcAddress'], value['dstAddress'], value['SYN'] 
        self.punch.spoofyTable[value['srcAddress']] = (value['dstAddress'], \
                                                       value['SYN'])
        
        if value['dstAddress'] in self.punch.spoofyTable:
            if self.punch.spoofyTable[value['srcAddress']]:
                b = Broker()
                b.fakeConnection(self.punch.spoofyTable, value['srcAddress'], value['dstAddress'])   
                del self.punch.spoofyTable[value['srcAddress']]
                del self.punch.spoofyTable[value['dstAddress']]


class Broker(Protocol):
    """Broke the NAT firewall sending spoofed SYNACK packet"""

    def __init__(self):
        pass

    #=================================================================
    def fakeConnection(self, table, user1, user2):
        users = (user1, user2)
        for i in (0, 1):
            user1 =  users[i%2]
            user2 =  users[(i+1)%2]

            dhost = user2[0]   # The remote host
            shost = user1[0]   # The source host
            dport = user2[1]   # The destination port
            sport = user1[1]   # The source port
            
            SYN = table[user1][1]
            ACK = table[user2][1]+1
                            
            # Create a new IP packet and set its source and destination addresses.
            #print 'IPs:', shost, dhost
            ip = ImpactPacket.IP()
            ip.set_ip_src(shost)
            ip.set_ip_dst(dhost)
            
            # Create a new TCP
            tcp = ImpactPacket.TCP()
            
            # Set the parameters for the connection
            #print 'Ports:', sport, dport
            tcp.set_th_sport(sport)
            tcp.set_th_dport(dport)
            #print 'SYN-ACK:', SYN, ACK
            print 'Send %s:%d (%ld) --> %s:%d (%ld)'%(shost, sport, SYN, dhost, dport, ACK)
            tcp.set_th_seq(SYN)
            tcp.set_SYN()
            tcp.set_th_ack(ACK)
            tcp.set_ACK()
            
            tcp.set_th_win(6)
        
        
            # Have the IP packet contain the TCP packet
            ip.contains(tcp)
            
            # Open a raw socket. Special permissions are usually required.
            protocol_num = socket.getprotobyname('tcp')
            self.s = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol_num)
            self.s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            #self._bind()

            # Calculate its checksum.
            tcp.calculate_checksum()
            tcp.auto_checksum = 1

            # Send it to the target host.
            self.s.sendto(ip.get_packet(), (dhost, dport))


 
