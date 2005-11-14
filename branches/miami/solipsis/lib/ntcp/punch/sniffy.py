import sys
import string
from threading import Thread

import pcapy
from pcapy import findalldevs, open_live
import impacket
from impacket.ImpactDecoder import EthDecoder, LinuxSLLDecoder

class DecoderThread(Thread):
    def __init__(self, pcapObj, udp_obj):
        self.udp_obj = udp_obj 
        # Query the type of the link and instantiate a decoder accordingly.
        datalink = pcapObj.datalink()
        if pcapy.DLT_EN10MB == datalink:
            self.decoder = EthDecoder()
        elif pcapy.DLT_LINUX_SLL == datalink:
            self.decoder = LinuxSLLDecoder()
        else:
            raise Exception("Datalink type not supported: " % datalink)

        self.pcap = pcapObj
        Thread.__init__(self)

    def run(self):
        """Sniff ad infinitum.
        PacketHandler shall be invoked by pcap for every packet.
        """
        self.pcap.loop(1, self.packetHandler)

    def packetHandler(self, hdr, data):
        """Use the ImpactDecoder to turn the rawpacket into a hierarchy
        of ImpactPacket instances.
        Display the packet in human-readable form.
        """
        try:
            packet = self.decoder.decode(data)
            #print 'Try to send SYN...'
            syn = packet.child().child().get_th_seq()
            self.udp_obj.send_SYN_to_ConnectionBroker(syn)
        except:
            print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]

def getInterface():
    """
    Grab a list of interfaces that pcap is able to listen on.
    The current user will be able to listen from all returned interfaces,
    using open_live to open them.
    """
    ifs = findalldevs()

    if sys.platform == 'win32':
        ifs = ifs[0].encode('utf-16')
        ifs = ifs.split('\x00')
        # TODO: listen on any interface
        return ifs[1]
    
    # No interfaces available, abort.
    if 0 == len(ifs):
        print "You don't have enough permissions to open any interface on this system."
        sys.exit(1)

    # Only one interface available, use it.
    elif 1 == len(ifs):
        print 'Only one interface present, defaulting to it.'
        return ifs[0]


    return 'any'


def sniff(argv, udp_obj, connector):
    """
    Starts to sniff for packet defined in argv filter

    @param argv: the string with a filter
    @param udp_obj: an udp objct to communicate with CB
    @param connector: to call the client factory functions
    """

    try:
        sys.argv = argv
        if len(sys.argv) < 3:
            print 'usage: sniff.py <interface> <expr>'
            sys.exit(0)

        dev = getInterface()

        # Open interface for catpuring.
        p = open_live(dev, 1500, 0, 100)

        # Set the BPF filter. See tcpdump(3).
        filter = ' '.join(sys.argv[2:])
        p.setfilter(filter)

##         print "Listening on %s: net=%s, mask=%s, linktype=%d" % (dev, p.getnet(), p.getmask(), p.datalink())

        # Start sniffing thread and finish main thread.
        DecoderThread(p, udp_obj).start()
    except:
        connector.method = 'sniff'
        connector.clientConnectionFailed(connector.punch, 'STUNT1: impossible to travers the NATs. You probably have not administrator privileges')
        return
        
