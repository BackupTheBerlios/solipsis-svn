
import sys
import logging

from nodeconnector import NodeConnector


class Bootstrap(object):
    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params
        self.node_connector = NodeConnector(reactor, params)
        self.node = self.node_connector.node

    def Run(self):
        reactor.listenUDP(self.params.port, self.node_connector)
        reactor.run()
