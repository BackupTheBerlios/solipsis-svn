
from socket import socket, AF_INET, SOCK_DGRAM
import sys, select

from solipsis.node.connector import Connector
from solipsis.util.address import Address
from solipsis.node.event import EventFactory
from solipsis.node.controlevent import ControlEvent


class UDPConnector(Connector):
    """ Connection using UDP sockets """
    def __init__(self, parser, eventQueue, params):
        """ Constructor.
        parser : the Parser object used to parse the events going through this connector
        eventQueue : queue used to communicate with other thread. The PeerConnector
        fills this queue with events. Other threads are responsible for reading and
        removing events from this queue
        netParams : initialization parameters of this class -
        a list [ buffer_size, logger_object ]
        """
        super(UDPConnector, self).__init__(parser, eventQueue)

        self.BUFFER_SIZE = params.buffer_size
        self.host = params.host
        self.port = params.port

        # network socket
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def run(self):
        """ Receive messages from other nodes and process them.
        Send messages to other nodes.
        """

        try:
            try:
                self.socket.bind((self.host, self.port))
                self.socket.setblocking(0)
                self.logger.debug("UDP connector started:" + str(self.socket.getsockname()))

                while not self.stopThread:

                    data = ""
                    # send outgoing messages
                    if not self.outgoing.empty():
                        e = self.outgoing.get()
                        self._send_no_wait(e)

                    readsock, writesock, errsock = select.select([self.socket], [], [], 2)

                    if len(readsock):
                        try:
                            # receive and process message from other nodes
                            data, sender = self.socket.recvfrom(self.BUFFER_SIZE)
                            if len(data) > 0:
                                self.logger.debug("recvfrom %s:%s: %s", sender[0],
                                                sender[1],data)

                                # Parse data and create a new event
                                netEvent = self.parser.createEvent(data)

                                # store ip address and port of sender
                                netEvent.setSenderAddress(Address(sender[0], sender[1]))

                                # add a new event to the queue of events that need to be
                                # processed
                                self.incoming.put(netEvent)
                        except ValueError:
                            self.logger.warn("NetThread - parsing error - unknown message " + data)
                        except:
                            self.logger.debug("Exception in network thread - " +
                                            str(sys.exc_info()[0]))
                            raise

            except Exception, e:
                evt = EventFactory.getInstance(ControlEvent.TYPE).createABORT('UDP connector error-' +
                                                                              str(e))
                self.incoming.put(evt)
                raise

        finally:
            self.socket.close()
            self.logger.info('End of Network Server...')
            sys.exit(0)

    def send(self, netEvent):
        """ Send a message to a peer
        To avoid problems when different thread access the socket object, only the
        network thread can send messages. As this method can be called by other
        threads, the message is NOT sent here. The message is instead added to a
        queue, and will be sent later by the network thread
        """
        #self.outgoing.put(netEvent)
        self._send_no_wait(netEvent)

    def _send_no_wait(self, netEvent):
        """ Send a message
        Immediatly send a message. This method must only be called from the network
        thread.
        """
        address =  netEvent.getRecipientAddress()
        host = address.getHost()
        port = address.getPort()
        data = ""
        data = self.parser.getData(netEvent)
        self.logger.debug("_send_no_wait %s %d - %s", host, port, data)
        try:
            self.socket.sendto(self.parser.getData(netEvent), (host, port))
        except:
            self.logger.critical("Error in udpconnector._send_no_wait %s %s" % (host, port))
            raise


