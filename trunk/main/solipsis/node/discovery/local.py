
import socket

import twisted.internet.defer as defer


def DiscoverAddress(reactor, params):
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception, e:
        return defer.fail(e)
    else:
        return defer.succeed(ip)
