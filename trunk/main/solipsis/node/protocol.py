
import re
import new
import logging

from solipsis.util.exception import *
from solipsis.util.geometry import Position
from solipsis.util.address import Address

VERSION = 1.0
BANNER = "SOLIPSIS/" + `VERSION`


#
# This is a list of allowed arguments in the Solipsis protocol.
# Each tuple has several field:
# - internal variable name to uniquely identify each argument
#   (e.g. protocol.ARG_ID)
# - full parameter string used in the Solipsis protocol
# - attribute name used when creating messages
#
_args = [
    ('ARG_ADDRESS', 'Address', 'address'),
    ('ARG_AWARENESS_RADIUS', 'Awareness-Radius', 'awareness_radius'),
    ('ARG_BEST_DISTANCE', 'Best-Distance', 'best_distance'),
    ('ARG_BEST_ID', 'Best-Id', 'best_id'),
    ('ARG_CALIBRE', 'Calibre', 'calibre'),
    ('ARG_CLOCKWISE', 'Clockwise', 'clockwise'),
    ('ARG_ID', 'Id', 'id_'),
    ('ARG_ORIENTATION', 'Orientation', 'orientation'),
    ('ARG_POSITION', 'Position', 'position'),
    ('ARG_PSEUDO', 'Pseudo', 'pseudo'),

    ('ARG_REMOTE_ADDRESS', 'Remote-Address', 'remote_address'),
    ('ARG_REMOTE_AWARENESS_RADIUS', 'Remote-Awareness-Radius', 'remote_awareness_radius'),
    ('ARG_REMOTE_CALIBRE', 'Remote-Calibre', 'remote_calibre'),
    ('ARG_REMOTE_ID', 'Remote-Id', 'remote_id'),
    ('ARG_REMOTE_ORIENTATION', 'Remote-Orientation', 'remote_orientation'),
    ('ARG_REMOTE_POSITION', 'Remote-Position', 'remote_position'),
    ('ARG_REMOTE_PSEUDO', 'Remote-Pseudo', 'remote_pseudo'),
    ('ARG_SERVICE_ADDRESS', 'Service-Address', 'service_address'),
    ('ARG_SERVICE_DESC', 'Service-Desc', 'service_desc'),
    ('ARG_SERVICE_ID', 'Service-Id', 'service_id'),
]

def _init_args(args):
    from itertools import count, izip
    global ALL_ARGS, ATTRIBUTE_NAMES, PROTOCOL_STRINGS

    ALL_ARGS = []
    ATTRIBUTE_NAMES = {}
    PROTOCOL_STRINGS = {}

    for c, (arg_name, full_string, attr_name) in izip(count(1), args):
        arg_value = full_string
        #arg_value = c
        globals()[arg_name] = arg_value
        ALL_ARGS.append(arg_value)
        ATTRIBUTE_NAMES[arg_value] = attr_name
        PROTOCOL_STRINGS[arg_value] = full_string

_init_args(_args)


#
# Syntax definition for each protocol argument.
# This is mandatory.
#
_syntax_table = {
    ARG_ADDRESS          : '\s*.*:\d+\s*',
    ARG_AWARENESS_RADIUS : '\d+',
    ARG_CLOCKWISE        : '[-+]1',
    ARG_CALIBRE          : '\d{1,4}',
    ARG_BEST_DISTANCE    : '\d+',
    ARG_ID               : '[^\s]*',
    ARG_ORIENTATION      : '\d{1,3}',
    ARG_POSITION         : '\s*\d+\s*,\s*\d+\s*,\s*\d+\s*',
    ARG_PSEUDO           : '.*',
}
_aliases = {
    ARG_BEST_ID:                    ARG_ID,
    ARG_REMOTE_ADDRESS:             ARG_ADDRESS,
    ARG_REMOTE_AWARENESS_RADIUS:    ARG_AWARENESS_RADIUS,
    ARG_REMOTE_CALIBRE:             ARG_CALIBRE,
    ARG_REMOTE_ID:                  ARG_ID,
    ARG_REMOTE_ORIENTATION:         ARG_ORIENTATION,
    ARG_REMOTE_POSITION:            ARG_POSITION,
    ARG_REMOTE_PSEUDO:              ARG_PSEUDO,
}

def _init_syntax(syntaxes, syntax_aliases):
    global ARGS_SYNTAX
    ARGS_SYNTAX = {}

    for arg, pattern in syntaxes.items():
        ARGS_SYNTAX[arg] = re.compile('^' + pattern + '$')
    for alias, arg in syntax_aliases.items():
        ARGS_SYNTAX[alias] = ARGS_SYNTAX[arg]

_init_syntax(_syntax_table, _aliases)


#
# Constructor function for each argument
# This is mandatory.
#
_constructor_table = {
    ARG_CLOCKWISE : (lambda x: int(x) > 0),
    ARG_POSITION : (lambda s: Position(strPosition=s)),
    ARG_ADDRESS : (lambda s: Address(strAddress=s)),
    ARG_CALIBRE : int,
    ARG_ORIENTATION : int,
    ARG_PSEUDO : str,
    ARG_AWARENESS_RADIUS : long,
    ARG_BEST_DISTANCE : long,
    ARG_ID : str,
}

def _init_constructor(constructors, constructor_aliases):
    global ARGS_CONSTRUCTOR
    ARGS_CONSTRUCTOR = {}

    for arg, fun in constructors.items():
        ARGS_CONSTRUCTOR[arg] = fun
    for alias, arg in constructor_aliases.items():
        ARGS_CONSTRUCTOR[alias] = ARGS_CONSTRUCTOR[arg]

_init_constructor(_constructor_table, _aliases)


#
# Declaration of mandatory arguments for each protocol request
#
ALL_NODE_ARGS = [
    ARG_ADDRESS,
    ARG_AWARENESS_RADIUS,
    ARG_CALIBRE,
    ARG_ID,
    ARG_ORIENTATION,
    ARG_POSITION,
    ARG_PSEUDO,
]

ALL_REMOTE_ARGS = [
    ARG_REMOTE_ADDRESS,
    ARG_REMOTE_AWARENESS_RADIUS,
    ARG_REMOTE_CALIBRE,
    ARG_REMOTE_ID,
    ARG_REMOTE_ORIENTATION,
    ARG_REMOTE_POSITION,
    ARG_REMOTE_PSEUDO,
]

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
    'QUERYAROUND': [ ARG_ID, ARG_POSITION, ARG_BEST_ID, ARG_BEST_DISTANCE ],
    'SEARCH'     : [ ARG_ID, ARG_CLOCKWISE ],
    'SERVICE'    : [ ARG_ID, ARG_SERVICE_ID, ARG_SERVICE_DESC, ARG_SERVICE_ADDRESS ],
    'UPDATE'     : ALL_NODE_ARGS,
}


def checkMessage(data):
    message = Message()
    try:
        message.fromData(data, parse_only=True)
        return True
    except:
        raise
        return False


class Message(object):
    """
    This class represents a Solipsis message.
    """

    request_syntax = re.compile(r'^\s*(\w+)\s+SOLIPSIS/(\d+\.\d+)\s*$')
    argument_syntax = re.compile(r'^\s*([-\w]+)\s*:\s*(.*?)\s*$')

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

    def fromData(self, data, parse_only=False):
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
        m = self.request_syntax.match(lines[0])
        if m is None:
            raise EventParsingError("Invalid request syntax: " + lines[0])

        # Request is first word of the first line (e.g. NEAREST, or BEST ...)
        request = m.group(1).upper()
        # Extract protocol version
        version = float(m.group(2))

        # Basic sanity check
        if version > VERSION:
            raise EventParsingError("Unexpected protocol version: %s" % str(version))
        elif version < VERSION:
            self.logger.info("Received message from older protocol version: %s" % str(version))
        if not request in REQUESTS:
            raise EventParsingError("Unknown request: " + request)

        # Get args for this request
        mandatory_args = REQUESTS[request]
        missing_args = dict.fromkeys(mandatory_args)

        # Now let's parse each parameter line in turn
        for line in lines[1:]:
            m = self.argument_syntax.match(line)
            if m is None:
                raise EventParsingError("Invalid message syntax:\r\n" + data)

            # Get arg name and arg value
            name = m.group(1)
            value = m.group(2)

            # Each arg has its own syntax-checking regex
            # (e.g. for a calibre we expect a 3-digit number)
            try:
                arg_syntax = ARGS_SYNTAX[name]
            except KeyError:
                raise EventParsingError("Unknown arg '%s'" % (name))
            if not arg_syntax.match(value):
                raise EventParsingError("Invalid arg syntax for '%s': '%s'" % (name, value))

            # The syntax is correct => add this arg to the arg list
            if name in args:
                raise EventParsingError("Duplicate value for arg '%s'" % name)

            # Build argument value from its registered constructor
            if not parse_only:
                #args[ATTRIBUTE_NAMES] = ARGS_CONSTRUCTOR[name](value)
                args[name] = ARGS_CONSTRUCTOR[name](value)

            # Log optional arguments
            if name in missing_args:
                del missing_args[name]
            else:
                self.logger.debug("Optional argument '%s' in message '%s'" % (name, request))

        # Check that all required fields have been encountered
        if missing_args:
            raise EventParsingError("Missing arguments (%s) in message '%s'"
                    % (",".join([`arg` for arg in missing_args]), request))

        # Everything's ok
        self.request = request
        self.args = args
        self.data = data
        return True


if __name__ == '__main__':
    data = ("HEARTBEAT SOLIPSIS/1.0\r\n" +
            "Id: 192.168.0.1\r\n" +
            "Position: 455464, 78785425, 0\r\n" +
            "\r\n")
    message = Message()
    print message.fromData(data)
    print message.toData()
    print message.fromData(message.toData())


