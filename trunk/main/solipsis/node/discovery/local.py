
import socket

import twisted.internet.defer as defer


def DiscoverAddress(port, reactor, params):
    try:
        host = socket.gethostbyname(socket.gethostname())
    except Exception, e:
        return defer.fail(e)
    else:
        return defer.succeed((host, port))
