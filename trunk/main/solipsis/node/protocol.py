# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>

import re
import new
import logging

try:
    set
except:
    from sets import Set as set

from solipsis.util.exception import *
from solipsis.util.geometry import Position
from solipsis.util.address import Address
from solipsis.util.bidict import bidict
from entity import Service

VERSION = 1.0
BANNER = "SOLIPSIS/" + `VERSION`
CHARSET = "utf-8"

#
# This is a list of allowed arguments in the Solipsis protocol.
# Each tuple has several fields:
# - internal id to uniquely identify each argument
#   (e.g. protocol.ARG_ID)
# - full parameter string used in the Solipsis protocol
# - attribute name used when creating messages
#
_args = [
    ('ARG_ADDRESS', 'Address', 'address'),
    ('ARG_AWARENESS_RADIUS', 'Awareness-Radius', 'awareness_radius'),
    ('ARG_BEST_DISTANCE', 'Best-Distance', 'best_distance'),
    ('ARG_BEST_ID', 'Best-Id', 'best_id'),
    ('ARG_CLOCKWISE', 'Clockwise', 'clockwise'),
    ('ARG_HOLD_TIME', 'Hold-Time', 'hold_time'),
    ('ARG_ID', 'Id', 'id_'),
    ('ARG_POSITION', 'Position', 'position'),
    ('ARG_SEND_DETECTS', 'Send-Detects', 'send_detects'),

    ('ARG_REMOTE_ADDRESS', 'Remote-Address', 'remote_address'),
    ('ARG_REMOTE_AWARENESS_RADIUS', 'Remote-Awareness-Radius', 'remote_awareness_radius'),
    ('ARG_REMOTE_ID', 'Remote-Id', 'remote_id'),
    ('ARG_REMOTE_POSITION', 'Remote-Position', 'remote_position'),
    ('ARG_REMOTE_PSEUDO', 'Remote-Pseudo', 'remote_pseudo'),

    ('ARG_ACCEPT_LANGUAGES', 'Languages', 'accept_languages'),
    ('ARG_ACCEPT_SERVICES', 'Services', 'accept_services'),
    ('ARG_PSEUDO', 'Pseudo', 'pseudo'),
    ('ARG_SERVICE_ADDRESS', 'Service-Address', 'service_address'),
    ('ARG_SERVICE_ID', 'Service-Id', 'service_id'),
]

def _init_args(args):
    from itertools import count, izip
    global ALL_ARGS, ATTRIBUTE_NAMES, PROTOCOL_STRINGS

    ALL_ARGS = []
    ATTRIBUTE_NAMES = bidict()
    PROTOCOL_STRINGS = bidict()

    for c, (arg_const, full_string, attr_name) in izip(count(1), args):
        arg_id = c
        globals()[arg_const] = arg_id
        ALL_ARGS.append(arg_id)
        ATTRIBUTE_NAMES[arg_id] = intern(attr_name)
        PROTOCOL_STRINGS[arg_id] = intern(full_string)

_init_args(_args)

_aliases = {
    ARG_BEST_ID:                    ARG_ID,
    ARG_REMOTE_ADDRESS:             ARG_ADDRESS,
    ARG_REMOTE_AWARENESS_RADIUS:    ARG_AWARENESS_RADIUS,
    ARG_REMOTE_ID:                  ARG_ID,
    ARG_REMOTE_POSITION:            ARG_POSITION,
    ARG_REMOTE_PSEUDO:              ARG_PSEUDO,
}

def _init_table(table_name, table, aliases=_aliases, transform=(lambda x: x)):
    # Create a global table of the specified name, then fill it with values
    t = {}
    globals()[table_name] = t

    for k, v in table.items():
        t[k] = transform(v)
    for k, v in aliases.items():
        if not k in t:
            t[k] = t[v]


#
# Syntax definition for each protocol argument.
# This is mandatory.
#

_syntax_table = {
    ARG_ACCEPT_LANGUAGES : r'([\w]+(\s*,\s*[\w]+)*)?',
    ARG_ACCEPT_SERVICES  : r'([-_/\w\d]+(;d=\w+)?(\s*,\s*[-_/\w\d]+(;d=\w+)?)*)?',
    ARG_ADDRESS          : r'\s*.*:\d+\s*',
    ARG_AWARENESS_RADIUS : r'\d+',
    ARG_CLOCKWISE        : r'[-+]1',
    ARG_BEST_DISTANCE    : r'\d+',
    ARG_HOLD_TIME        : r'[\d]+',
    ARG_ID               : r'[^\s]*',
    ARG_POSITION         : r'\s*\d+\s*,\s*\d+\s*,\s*\d+\s*',
    ARG_PSEUDO           : r'.*',
    ARG_SEND_DETECTS     : r'(now|later)',
    ARG_SERVICE_ADDRESS  : r'[^\s]*',
    ARG_SERVICE_ID       : r'[-_/\w\d]+',
}

_init_table('ARGS_SYNTAX', _syntax_table, transform=(lambda x: re.compile('^' + x + '$')))


#
# Constructor function for each argument
# This is mandatory.
#

def _accept_languages_from_string(s):
    return [l.strip() for l in s.split(',')]

def _accept_languages_to_string(l):
    return ", ".join(l)

def _accept_services_from_string(s):
    services = []
    for l in s.split(','):
        t = l.strip().split(';')
        id_ = t[0]
        if len(t) > 1 and t[1].startswith('d='):
            type = t[1][2:]
        else:
            type = 'bidir'
        services.append(Service(id_, type))
    return services

def _accept_services_to_string(services):
    s = []
    for service in services:
        if service.type == 'bidir':
            s.append("%s" % service.id_)
        else:
            s.append("%s;d=%s" % (service.id_, service.type))
    return ", ".join(s)

_from_string = {
    ARG_ACCEPT_LANGUAGES:   _accept_languages_from_string,
    ARG_ACCEPT_SERVICES:    _accept_services_from_string,
    ARG_ADDRESS:            (lambda s: Address(strAddress=s)),
    ARG_AWARENESS_RADIUS:   float,
    ARG_BEST_DISTANCE:      float,
    ARG_CLOCKWISE:          (lambda c: int(c) > 0),
    ARG_HOLD_TIME:          int,
    ARG_ID:                 intern,
    ARG_POSITION:           (lambda s: Position(strPosition=s)),
    ARG_PSEUDO:             (lambda s: unicode(s.decode(CHARSET))),
    ARG_SEND_DETECTS:       (lambda s: s == 'now'),
    ARG_SERVICE_ID:         str,
    ARG_SERVICE_ADDRESS:    (lambda a: str(a)),
}

_to_string = {
    ARG_ACCEPT_LANGUAGES:   _accept_languages_to_string,
    ARG_ACCEPT_SERVICES:    _accept_services_to_string,
    ARG_ADDRESS:            str,
    # TODO: change all coord and distance types to float
    ARG_AWARENESS_RADIUS:   (lambda x: str(long(x))),
    ARG_BEST_DISTANCE:      (lambda x: str(long(x))),
    ARG_CLOCKWISE:          (lambda c: c and "+1" or "-1"),
    ARG_HOLD_TIME:          str,
    ARG_ID:                 str,
    ARG_POSITION:           str,
    ARG_PSEUDO:             (lambda u: u.encode(CHARSET)),
    ARG_SEND_DETECTS:       (lambda x: x and "now" or "later"),
    ARG_SERVICE_ID:         str,
    ARG_SERVICE_ADDRESS:    (lambda a: a is not None and str(a) or ""),
}

_init_table('ARGS_FROM_STRING', _from_string)
_init_table('ARGS_TO_STRING', _to_string)


#
# Declaration of mandatory arguments for each protocol request
#
NODE_ARGS = [
    ARG_ADDRESS,
    ARG_AWARENESS_RADIUS,
    ARG_ID,
    ARG_POSITION,
]

REMOTE_ARGS = [
    ARG_REMOTE_ADDRESS,
    ARG_REMOTE_AWARENESS_RADIUS,
    ARG_REMOTE_ID,
    ARG_REMOTE_POSITION,
]

REQUESTS = {
    'CLOSE'      : [ ARG_ID ],
    'CONNECT'    : NODE_ARGS + [ ARG_HOLD_TIME ],
    'HEARTBEAT'  : [ ARG_ID ],
    'HELLO'      : NODE_ARGS + [ ARG_HOLD_TIME, ARG_SEND_DETECTS ],

    'AROUND'     : REMOTE_ARGS,
    'BEST'       : NODE_ARGS,
    'DETECT'     : REMOTE_ARGS,
    'FINDNEAREST': [ ARG_ID, ARG_ADDRESS, ARG_POSITION ],
    'FOUND'      : [ ARG_REMOTE_ID, ARG_REMOTE_ADDRESS, ARG_REMOTE_POSITION ],
    'NEAREST'    : [ ARG_REMOTE_ID, ARG_REMOTE_ADDRESS, ARG_REMOTE_POSITION ],
    'QUERYAROUND': [ ARG_ID, ARG_ADDRESS, ARG_POSITION, ARG_BEST_ID, ARG_BEST_DISTANCE ],
    'SEARCH'     : [ ARG_ID, ARG_CLOCKWISE ],
    'UPDATE'     : NODE_ARGS,

    'META'       : [ ARG_ID, ARG_PSEUDO, ARG_ACCEPT_LANGUAGES, ARG_ACCEPT_SERVICES ],
    'QUERYMETA'  : [ ARG_ID, ARG_PSEUDO, ARG_ACCEPT_LANGUAGES, ARG_ACCEPT_SERVICES ],
    'QUERYSERVICE': [ ARG_ID, ARG_SERVICE_ID, ARG_SERVICE_ADDRESS ],
    'SERVICEINFO': [ ARG_ID, ARG_SERVICE_ID, ARG_SERVICE_ADDRESS ],
}


class Message(object):
    """
    This structure is a simple representation of a Solipsis message.
    """
    class Args(object):
        pass

    def __init__(self, request = ""):
        self.request = request
        self.args = self.Args()


class Parser(object):
    """
    This class parses and builds Solipsis messages.
    """
    request_syntax = re.compile(r'^\s*(\w+)\s+SOLIPSIS/(\d+\.\d+)\s*$')
    argument_syntax = re.compile(r'^\s*([-\w]+)\s*:\s*(.*?)\s*$')

    def __init__(self):
        self.logger = logging.getLogger('root')

    def StripMessage(self, message):
        """
        Strip unnecessary parameters from message.
        """
        required_args = set([ATTRIBUTE_NAMES[arg_id] for arg_id in REQUESTS[message.request]])
        args = message.args
        for k in set(args.__dict__) - required_args:
            delattr(args, k)

    def BuildMessage(self, message):
        """
        Build protocol data from message.
        """
        lines = []
        args = message.args.__dict__

        # 1. Request and protocol version
        lines.append(message.request + " " + BANNER)
        # 2. Request arguments
        for k, v in args.iteritems():
            arg_id = ATTRIBUTE_NAMES.get_reverse(k)
            lines.append('%s: %s' % (PROTOCOL_STRINGS[arg_id], ARGS_TO_STRING[arg_id](v)))
        # 3. End of message (double CR-LF)
        data = "\r\n".join(lines) + "\r\n\r\n"
        # In debug mode, parse our own message to check it is well-formed
        assert self.ParseMessage(data, parse_only=True), "Bad generated message: " + data
        return data


    def ParseMessage(self, data, parse_only=False):
        """
        Parse and extract message from protocol data.
        """
        # Parse raw data to construct message (strip empty lines)
        lines = [line.strip() for line in data.splitlines() if line.strip() != ""]
        # If message is empty, return false
        if not lines:
            return None
        # Parse request line
        m = self.request_syntax.match(lines[0])
        if m is None:
            raise EventParsingError("Invalid request syntax: " + repr(lines[0]))

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
        args = {}

        # Now let's parse each parameter line in turn
        for line in lines[1:]:
            # Get arg name and arg value
            t = line.split(':', 1)
            if len(t) != 2:
                raise EventParsingError("Invalid message syntax:\r\n" + data)
            name = t[0].strip()
            value = t[1].strip()

            # Each arg has its own syntax-checking regex
            # (e.g. for a calibre we expect a 3-digit number)
            try:
                arg_id = PROTOCOL_STRINGS.get_reverse(name)
                arg_syntax = ARGS_SYNTAX[arg_id]
            except KeyError:
                raise EventParsingError("Unknown arg '%s'" % (name))
            if not arg_syntax.match(value):
                raise EventParsingError("Invalid arg syntax for '%s': '%s'" % (name, value))

            # The syntax is correct => add this arg to the arg list
            if arg_id in args:
                raise EventParsingError("Duplicate value for arg '%s'" % name)

            # Build argument value from its registered constructor
            if not parse_only:
                args[arg_id] = ARGS_FROM_STRING[arg_id](value)

            # Log optional arguments
            if arg_id in missing_args:
                del missing_args[arg_id]
            else:
                self.logger.debug("Optional argument '%s' in message '%s'" % (name, request))

        # Check that all required fields have been encountered
        if missing_args:
            raise EventParsingError("Missing arguments (%s) in message '%s'"
                    % (",".join([PROTOCOL_STRINGS[arg] for arg in missing_args]), request))

        # Everything's ok
        if not parse_only:
            message = Message()
            message.request = request
            for arg_id, value in args.iteritems():
                setattr(message.args, ATTRIBUTE_NAMES[arg_id], value)
            return message
        else:
            return True


if __name__ == '__main__':
    data = ("HEARTBEAT SOLIPSIS/1.0\r\n" +
            "Id: 192.168.0.1\r\n" +
            "Position: 455464, 78785425, 0\r\n" +
            "Clockwise: -1" +
            "\r\n")
    parser = Parser()
    message = parser.ParseMessage(data)
    print message.request
    print message.args.__dict__
    data = parser.BuildMessage(message)
    print data
    message = parser.ParseMessage(data)
    print message.args.__dict__
