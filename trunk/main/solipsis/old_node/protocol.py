
import re, new, logging

from solipsis.util.exception import *
from solipsis.util.geometry import PositionFactory
from solipsis.util.address import AddressFactory

VERSION = 1.0
BANNER = "SOLIPSIS/" + `VERSION`

ARG_ID = 'Id'
ARG_POSITION = 'Position'
ARG_ADDRESS = 'Address'
ARG_AWARENESS_RADIUS = 'Awareness-Radius'
ARG_CALIBRE = 'Calibre'
ARG_PSEUDO = 'Pseudo'
ARG_ORIENTATION = 'Orientation'
ARG_BEST_ID = 'Best-Id'
ARG_BEST_DISTANCE = 'Best-Distance'
ARG_REMOTE_ID = 'Remote-Id'
ARG_REMOTE_POSITION = 'Remote-Position'
ARG_REMOTE_ADDRESS = 'Remote-Address'
ARG_REMOTE_AWARENESS_RADIUS = 'Remote-Awareness-Radius'
ARG_REMOTE_CALIBRE = 'Remote-Calibre'
ARG_REMOTE_PSEUDO = 'Remote-Pseudo'
ARG_REMOTE_ORIENTATION = 'Remote-Orientation'
ARG_SERVICE_ID = 'Service-Id'
ARG_SERVICE_DESC = 'Service-Desc'
ARG_SERVICE_ADDRESS = 'Service-Address'
ARG_CLOCKWISE = 'Clockwise'

ALL_NODE_ARGS = [ ARG_ADDRESS, ARG_ID, ARG_POSITION, ARG_AWARENESS_RADIUS,
                  ARG_CALIBRE, ARG_ORIENTATION, ARG_PSEUDO ]

ALL_REMOTE_ARGS = [ ARG_REMOTE_ADDRESS, ARG_REMOTE_ID, ARG_REMOTE_POSITION,
                    ARG_REMOTE_AWARENESS_RADIUS, ARG_REMOTE_CALIBRE,
                    ARG_REMOTE_ORIENTATION, ARG_REMOTE_PSEUDO ]

REQUESTS = {
    'AROUND'     : ALL_REMOTE_ARGS,
    'BEST'       : ALL_NODE_ARGS,
    'CLOSE'      : [ ARG_ID ],
    'CONNECT'    : ALL_NODE_ARGS,
    'DETECT'     : ALL_REMOTE_ARGS,
    'ENDSERVICE' : [ ARG_ID, ARG_SERVICE_ID ],
    'FINDNEAREST': [ ARG_ID, ARG_POSITION ],
    'FOUND'      : ALL_REMOTE_ARGS,
    'HEARTBEAT'  : [ ARG_ID ],
    'HELLO'      : ALL_NODE_ARGS,
    'NEAREST'    : [ ARG_REMOTE_ADDRESS, ARG_REMOTE_POSITION ],
    'QUERYAROUND': [ ARG_POSITION, ARG_BEST_ID, ARG_BEST_DISTANCE ],
    'SEARCH'     : [ ARG_ID, ARG_CLOCKWISE ],
    'SERVICE'    : [ ARG_ID, ARG_SERVICE_ID, ARG_SERVICE_DESC, ARG_SERVICE_ADDRESS ],
    'UPDATE'     : ALL_NODE_ARGS
    }

ARGS_SYNTAX = {
    ARG_ADDRESS          : '\s*.*:\d+\s*',
    ARG_AWARENESS_RADIUS : '\d+',
    ARG_CLOCKWISE        : '[-+]1',
    ARG_CALIBRE          : '\d{1,4}',
    ARG_BEST_DISTANCE    : '\d+',
    ARG_ID               : '[^\s]*',
    ARG_ORIENTATION      : '\d{1,3}',
    ARG_POSITION         : '^\s*\d+\s*-\s*\d+\s*-\s*\d+\s*$',
    ARG_PSEUDO           : '.*'
    }


ARGS_SYNTAX[ARG_BEST_ID]                   = ARGS_SYNTAX[ARG_ID]
ARGS_SYNTAX[ARG_REMOTE_ADDRESS]            = ARGS_SYNTAX[ARG_ADDRESS]
ARGS_SYNTAX[ARG_REMOTE_AWARENESS_RADIUS]   = ARGS_SYNTAX[ARG_AWARENESS_RADIUS]
ARGS_SYNTAX[ARG_REMOTE_CALIBRE]            = ARGS_SYNTAX[ARG_CALIBRE]
ARGS_SYNTAX[ARG_REMOTE_ID]                 = ARGS_SYNTAX[ARG_ID]
ARGS_SYNTAX[ARG_REMOTE_ORIENTATION]        = ARGS_SYNTAX[ARG_ORIENTATION]
ARGS_SYNTAX[ARG_REMOTE_POSITION]           = ARGS_SYNTAX[ARG_POSITION]
ARGS_SYNTAX[ARG_REMOTE_PSEUDO]             = ARGS_SYNTAX[ARG_PSEUDO]

ARGS_CONSTRUCTOR = {
    ARG_CLOCKWISE : (lambda x: int(x) > 0),
    ARG_POSITION : PositionFactory.create,
    ARG_ADDRESS : AddressFactory.create,
    ARG_CALIBRE : int,
    ARG_ORIENTATION : int,
    ARG_PSEUDO : str,
    ARG_AWARENESS_RADIUS : int,
    ARG_BEST_DISTANCE : int,
    ARG_ID : str
    }

ARGS_CONSTRUCTOR[ARG_BEST_ID]                 = ARGS_CONSTRUCTOR[ARG_ID]
ARGS_CONSTRUCTOR[ARG_REMOTE_ADDRESS]          = ARGS_CONSTRUCTOR[ARG_ADDRESS]
ARGS_CONSTRUCTOR[ARG_REMOTE_AWARENESS_RADIUS] = ARGS_CONSTRUCTOR[ARG_AWARENESS_RADIUS]
ARGS_CONSTRUCTOR[ARG_REMOTE_CALIBRE]          = ARGS_CONSTRUCTOR[ARG_CALIBRE]
ARGS_CONSTRUCTOR[ARG_REMOTE_ID]               = ARGS_CONSTRUCTOR[ARG_ID]
ARGS_CONSTRUCTOR[ARG_REMOTE_ORIENTATION]      = ARGS_CONSTRUCTOR[ARG_ORIENTATION]
ARGS_CONSTRUCTOR[ARG_REMOTE_POSITION]         = ARGS_CONSTRUCTOR[ARG_POSITION]
ARGS_CONSTRUCTOR[ARG_REMOTE_PSEUDO]           = ARGS_CONSTRUCTOR[ARG_PSEUDO]

class Message(object):
    """
    This class represents a Solipsis message.
    """

    def __init__(self):
        self.logger = logging.getLogger('root')
        self.reset()

    def reset(self):
        self.request = None
        self.args = {}
        self.data = ""

    def toData(self):
        """
        Build protocol data from message.
        """

        lines = []
        # 1. Request and protocol version
        lines.append(self.request + " " + BANNER)
        # 2. Request arguments
        lines.extend(['%s: %s' % (arg, self.args[arg]) for arg in self.args])
        # 3. End of message (double CR-LF)
        data = "\r\n".join(lines) + "\r\n\r\n"
        # In debug mode, parse our own message to check it is well-formed
        assert checkMessage(data), "Bad generated message: " + data
        return data

    def fromData(self, data):
        """
        Parse and extract message from protocol data.
        """

        self.reset()
        request = ""
        version = None
        args = {}

        # Parse raw data to construct message (strip empty lines)
        lines = [line.strip() for line in data.splitlines() if line.strip() != ""]
        # If message is empty, return false
        if not lines:
            return False
        # Parse request line
        requestLinePattern = re.compile(r'^\s*(\w+)\s+SOLIPSIS/(\d+\.\d+)\s*$')
        requestLineMatch = requestLinePattern.match(lines[0])
        if requestLineMatch is None:
            raise EventParsingError("Invalid request syntax: " + lines[0])

        # Request is first word of the first line (e.g. NEAREST, or BEST ...)
        request = requestLineMatch.group(1).upper()
        # Extract protocol version
        version = float(requestLineMatch.group(2))

        # Basic sanity check
        if version > VERSION:
            raise EventParsingError("Unexpected protocol version: %s" % str(version))
        elif version < VERSION:
            self.logger.info("Received message from older protocol version: %s" % str(version))
        if not REQUESTS.has_key(request):
            raise EventParsingError("Unknown request: " + request)

        # Get args for this request
        argList = REQUESTS[request]

        # Now let's parse each parameter line in turn
        argPattern = re.compile(r'^\s*([-\w]+)\s*:\s*(.*?)\s*$')
        for line in lines[1:]:
            argMatch = argPattern.match(line)
            if argMatch is None:
                raise EventParsingError("Invalid message syntax:\r\n" + data)

            # Get arg name and arg value
            argName = argMatch.group(1)
            argVal = argMatch.group(2)

            # Log optional
            if argName not in argList:
                self.logger.debug("Optional argument '%s' in message '%s'" % (argName, request))

            # Each arg has its own syntax-checking regex
            # (e.g. for a calibre we expect a 3-digit number)
            if ARGS_SYNTAX.has_key(argName):
                argSyntax = re.compile('^' + ARGS_SYNTAX[argName] + '$')
            else:
                raise EventParsingError("Unknown arg '%s'" % (argName))
            if not argSyntax.match(argVal):
                raise EventParsingError("Invalid arg syntax for '%s': '%s'" % (argName, argVal))

            # The syntax is correct => add this arg to the arg list
            if args.has_key(argName):
                raise EventParsingError("Duplicate value for arg '%s'" % argName)
            #args[argName] =  eval(ARGS_CONSTRUCTOR[argName] + '(argVal)')
            args[argName] =  ARGS_CONSTRUCTOR[argName](argVal)

        # Check that all required fields have been encountered
        for argName in argList:
            if not args.has_key(argName):
                raise EventParsingError("Missing argument '%s' in message '%s'" % (argName, request))

        # Everything's ok
        self.request = request
        self.args = args
        self.data = data
        return True


def checkMessage(data):
    message = Message()
    try:
        message.fromData(data)
        return True
    except:
        raise
        return False


if __name__ == '__main__':
    data = ("HEARTBEAT SOLIPSIS/1.0\r\n" +
            "Id: 192.168.0.1\r\n" +
            "Position: 455464 - 78785425\r\n" +
            "\r\n")
    message = Message()
    print message.fromData(data)
    print message.toData()
    print message.fromData(message.toData())


