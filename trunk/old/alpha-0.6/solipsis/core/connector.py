from threading import Thread
import logging

from solipsis.util.container import NotificationQueue

class Connector(Thread):
    """ Generic class for connecting to another component(peer or navigator) """
    def __init__(self, parser, eventQueue):
        """ Constructor
        parser : the Parser object used to parse the events going in and out of this
        connector
        eventQueue : queue used to communicate with other thread. The Connector
        fills this queue with events. Other threads are responsible for reading and
        removing events from this queue
        """
        Thread.__init__(self)

        # Event queue used to communicate with other threads
        # these events comes from other entities through this connector
        # and will be processed by the node
        self.incoming = eventQueue

        # Message to send queue
        # the node has created an event that will be sent using this connector
        # to another entity
        self.outgoing = NotificationQueue()

        # this flag is set to True when we want to stop this thread
        self.stopThread = False

        # Parser object
        self.parser = parser

        # logger
        self.logger = logging.getLogger('root')


    def stop(self):
        """ Stop the network thread
        """
        self.stopThread = True

    def setParser(self, parser):
        """ Set the connector type.
        parser : the Parser object used to parse the events going through this connector
        """
        self.parser = parser


