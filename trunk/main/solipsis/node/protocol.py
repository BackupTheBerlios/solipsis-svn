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

VERSION = 1.0
BANNER = "SOLIPSIS/" + `VERSION`


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
    ('ARG_ID', 'Id', 'id_'),
    ('ARG_POSITION', 'Position', 'position'),
    ('ARG_SEND_DETECTS', 'Send-Detects', 'send_detects'),

    ('ARG_REMOTE_ADDRESS', 'Remote-Address', 'remote_address'),
    ('ARG_REMOTE_AWARENESS_RADIUS', 'Remote-Awareness-Radius', 'remote_awareness_radius'),
    ('ARG_REMOTE_ID', 'Remote-Id', 'remote_id'),
    ('ARG_REMOTE_POSITION', 'Remote-Position', 'remote_position'),
    ('ARG_REMOTE_PSEUDO', 'Remote-Pseudo', 'remote_pseudo'),

    ('ARG_ACCEPT_SERVICES', 'Accept-Services', 'accept_services'),
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
    ARG_ADDRESS          : '\s*.*:\d+\s*',
    ARG_AWARENESS_RADIUS : '\d+',
    ARG_CLOCKWISE        : '[-+]1',
    ARG_BEST_DISTANCE    : '\d+',
    ARG_ID               : '[^\s]*',
    ARG_POSITION         : '\s*\d+\s*,\s*\d+\s*,\s*\d+\s*',
    ARG_PSEUDO           : '.*',
    ARG_SEND_DETECTS     : '(now|later)',
}

_init_table('ARGS_SYNTAX', _syntax_table, transform=(lambda x: re.compile('^' + x + '$')))


#
# Constructor function for each argument
# This is mandatory.
#
_from_string = {
    ARG_ADDRESS: (lambda s: Address(strAddress=s)),
    ARG_AWARENESS_RADIUS: float,
    ARG_BEST_DISTANCE: float,
    ARG_CLOCKWISE: (lambda x: int(x) > 0),
    ARG_ID: intern,
    ARG_POSITION: (lambda s: Position(strPosition=s)),
    ARG_PSEUDO: str,
    ARG_SEND_DETECTS: (lambda s: s=='now'),
}

_to_string = {
    ARG_ADDRESS: str,
    # TODO: change all coord and distance types to float
    ARG_AWARENESS_RADIUS: (lambda x: str(long(x))),
    ARG_BEST_DISTANCE: (lambda x: str(long(x))),
    ARG_CLOCKWISE: (lambda x: x and "+1" or "-1"),
    ARG_ID: str,
    ARG_POSITION: str,
    ARG_PSEUDO: str,
    ARG_SEND_DETECTS: (lambda x: x and "now" or "later"),
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
    'CONNECT'    : NODE_ARGS + [ ARG_PSEUDO ],
    'HEARTBEAT'  : [ ARG_ID ],
    'HELLO'      : NODE_ARGS + [ ARG_PSEUDO, ARG_SEND_DETECTS ],

    'AROUND'     : REMOTE_ARGS,
    'BEST'       : NODE_ARGS,
    'DETECT'     : REMOTE_ARGS,
    'FINDNEAREST': [ ARG_ID, ARG_ADDRESS, ARG_POSITION ],
    'FOUND'      : [ ARG_REMOTE_ID, ARG_REMOTE_ADDRESS, ARG_REMOTE_POSITION ],
    'NEAREST'    : [ ARG_REMOTE_ID, ARG_REMOTE_ADDRESS, ARG_REMOTE_POSITION ],
    'QUERYAROUND': [ ARG_ID, ARG_ADDRESS, ARG_POSITION, ARG_BEST_ID, ARG_BEST_DISTANCE ],
    'SEARCH'     : [ ARG_ID, ARG_CLOCKWISE ],
    'UPDATE'     : NODE_ARGS,

    'META'       : [ ARG_ID, ARG_PSEUDO, ARG_ACCEPT_SERVICES ],
    'QUERYMETA'  : [ ARG_ID, ARG_PSEUDO, ARG_ACCEPT_SERVICES ],
    'QUERYSERVICE': [ ARG_ID, ARG_SERVICE_ID, ARG_SERVICE_ADDRESS ],
    'SERVICEINFO': [ ARG_ID, ARG_SERVICE_ID, ARG_SERVICE_ADDRESS ],
}


class Message(object):
    class Args(object):
        pass

    def __init__(self, request = ""):
        self.request = request
        self.args = self.Args()


class Parser(object):
    """
    This class represents a Solipsis message.
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
            raise EventParsingError("Invalid request syntax: " + lines[0])

        # Request is first word of the first line (e.g. NEAREST, or BEST ...)
        reques