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
# <PYLINT>
# pylint: disable-msg=E0602
# (disable "Undefined variable" for dynamically created global variables...)
# </PYLINT>


import re
from copy import deepcopy

from solipsis.util.utils import set, safe_str, safe_unicode
from solipsis.util.exception import *
from solipsis.util.position import Position
from solipsis.util.address import Address
from solipsis.util.bidict import bidict
from solipsis.util.entity import Service

# Public API
__all__ = [
    # Constants
    'VERSION', 'BETTER_VERSION', 'SAFE_VERSION', 'BANNER', 'CHARSET',
    # Associative mappings,
    'ALL_ARGS', 'ATTRIBUTE_NAMES', 'PROTOCOL_STRINGS',
    # Request types table,
    'REQUESTS',
    # Attribute checkers and converters,
    'ARGS_SYNTAX', 'ARGS_FROM_STRING', 'ARGS_TO_STRING',
    # Classes
    'Message',
]


# The highest supported version
VERSION = 1.1
# The lowest version we try to negotiate with peers
BETTER_VERSION = 1.1
# The lowest supported version
SAFE_VERSION = 1.0

BANNER = "SOLIPSIS/"
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
    ('ARG_ID', 'Id', 'id_'),
    ('ARG_POSITION', 'Position', 'position'),
    ('ARG_VERSION', 'Version', 'version'),

    ('ARG_HOLD_TIME', 'Hold-Time', 'hold_time'),
    ('ARG_NEEDS_MIDDLEMAN', 'Needs-Middleman', 'needs_middleman'),
    ('ARG_SEND_DETECTS', 'Send-Detects', 'send_detects'),

    ('ARG_REMOTE_ADDRESS', 'Remote-Address', 'remote_address'),
    ('ARG_REMOTE_AWARENESS_RADIUS', 'Remote-Awareness-Radius', 'remote_awareness_radius'),
    ('ARG_REMOTE_ID', 'Remote-Id', 'remote_id'),
    ('ARG_REMOTE_POSITION', 'Remote-Position', 'remote_position'),
    ('ARG_REMOTE_VERSION', 'Remote-Version', 'remote_version'),

    ('ARG_REMOTE_NEEDS_MIDDLEMAN', 'Remote-Needs-Middleman', 'remote_needs_middleman'),

    ('ARG_ACCEPT_LANGUAGES', 'Languages', 'accept_languages'),
    ('ARG_ACCEPT_SERVICES', 'Services', 'accept_services'),
    ('ARG_PSEUDO', 'Pseudo', 'pseudo'),
    ('ARG_SERVICE_ADDRESS', 'Service-Address', 'service_address'),
    ('ARG_SERVICE_ID', 'Service-Id', 'service_id'),

    # This special argument is parsed separately
    ('ARG_PAYLOAD', '', 'payload'),
]

# An array of all argument numbers
ALL_ARGS = []
# An argument number <-> attribute name map
ATTRIBUTE_NAMES = bidict()
# An argument number <-> protocol header map
PROTOCOL_STRINGS = bidict()

def _init_args(args):
    from itertools import count, izip
    global ALL_ARGS, ATTRIBUTE_NAMES, PROTOCOL_STRINGS

    for c, (arg_const, full_string, attr_name) in izip(count(1), args):
        arg_id = c
        globals()[arg_const] = arg_id
        # Setup mappings between arg_id and different representations
        ATTRIBUTE_NAMES[arg_id] = intern(attr_name)
        PROTOCOL_STRINGS[arg_id] = intern(full_string)
        # Populate public API with a global var representing the argument type
        ALL_ARGS.append(arg_id)
        __all__.append(arg_const)

_init_args(_args)

# Aliases are helpers to apply the same syntax rules to different parameters
_aliases = {
    ARG_BEST_ID:                    ARG_ID,
    ARG_REMOTE_ADDRESS:             ARG_ADDRESS,
    ARG_REMOTE_AWARENESS_RADIUS:    ARG_AWARENESS_RADIUS,
    ARG_REMOTE_ID:                  ARG_ID,
    ARG_REMOTE_NEEDS_MIDDLEMAN:     ARG_NEEDS_MIDDLEMAN,
    ARG_REMOTE_POSITION:            ARG_POSITION,
    ARG_REMOTE_VERSION:             ARG_VERSION,
}

def _init_table(table, aliases=_aliases, transform=(lambda x: x)):
    # Create a global table of the specified name, then fill it with values
    t = {}
    for k, v in table.items():
        t[k] = transform(v)
    for k, v in aliases.items():
        if not k in t:
            t[k] = t[v]
    return t


#
# Syntax definition for each protocol argument.
# This is mandatory.
#

_syntax_table = {
    # Comma separated list of languages
    ARG_ACCEPT_LANGUAGES : r'([\w]+(\s*,\s*[\w]+)*)?',
    # Comma separated list of services with optional qualifier
    ARG_ACCEPT_SERVICES  : r'([-_/\w\d]+(;d=\w+)?(\s*,\s*[-_/\w\d]+(;d=\w+)?)*)?',
    # "Host:port" tuple
    ARG_ADDRESS          : r'\s*.*:\d+\s*',
    # Long integer
    ARG_AWARENESS_RADIUS : r'\d+',
    # Long integer
    ARG_BEST_DISTANCE    : r'\d+',
    # -1 or +1
    ARG_CLOCKWISE        : r'[-+]1',
    # Integer
    ARG_HOLD_TIME        : r'[\d]+',
    # String without space characters
    ARG_ID               : r'[^\s]*',
    # "yes" or "no"
    ARG_NEEDS_MIDDLEMAN  : r'(yes|no)',
    # Comma separated tuple of three long integers
    ARG_POSITION         : r'\s*\d+\s*,\s*\d+\s*,\s*\d+\s*',
    # Anything
    ARG_PSEUDO           : r'.*',
    # "now" or "later"
    ARG_SEND_DETECTS     : r'(now|later)',
    # String wihout space characters
    ARG_SERVICE_ADDRESS  : r'[^\s]*',
    # String of latin alphabet characters, digits and hyphens/underscores
    ARG_SERVICE_ID       : r'[-_/\w\d]+',
    # Floating point number
    ARG_VERSION          : r'\d+\.\d+',
}

ARGS_SYNTAX = _init_table(_syntax_table,
    transform=(lambda x: re.compile('^' + x + '$'))
    )


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
        id_ = t[0].strip()
        # Don't accept empty service ids
        # (this also handles the "no services" case)
        if not id_:
            continue
        if len(t) > 1 and t[1].startswith('d='):
            type = t[1][2:]
        else:
            type = 'bidir'
        service = Service(id_, type)
        # The service is not known until we receive detailed information
        service.known = False
        services.append(service)
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
    ARG_ADDRESS:            (lambda s: Address.FromString(s)),
    ARG_AWARENESS_RADIUS:   float,
    ARG_BEST_DISTANCE:      float,
    ARG_CLOCKWISE:          (lambda c: int(c) > 0),
    ARG_HOLD_TIME:          int,
    ARG_ID:                 intern,
    ARG_NEEDS_MIDDLEMAN:    (lambda s: s == "yes"),
    ARG_POSITION:           (lambda s: Position.FromString(s)),
    ARG_PSEUDO:             (lambda s: safe_unicode(s, CHARSET)),
    ARG_SEND_DETECTS:       (lambda s: s == 'now'),
    ARG_SERVICE_ID:         str,
    ARG_SERVICE_ADDRESS:    (lambda a: str(a)),
    ARG_VERSION:            (lambda v: float(v)),
}

_to_string = {
    ARG_ACCEPT_LANGUAGES:   _accept_languages_to_string,
    ARG_ACCEPT_SERVICES:    _accept_services_to_string,
    ARG_ADDRESS:            (lambda a: a.ToString()),
    ARG_AWARENESS_RADIUS:   (lambda x: str(long(x))),
    ARG_BEST_DISTANCE:      (lambda x: str(long(x))),
    ARG_CLOCKWISE:          (lambda c: c and "+1" or "-1"),
    ARG_HOLD_TIME:          str,
    ARG_ID:                 str,
    ARG_NEEDS_MIDDLEMAN:    (lambda x: x and "yes" or "no"),
    ARG_POSITION:           (lambda p: p.ToString()),
    ARG_PSEUDO:             (lambda u: safe_str(u, CHARSET)),
    ARG_SEND_DETECTS:       (lambda x: x and "now" or "later"),
    ARG_SERVICE_ID:         str,
    ARG_SERVICE_ADDRESS:    (lambda a: a is not None and str(a) or ""),
    ARG_VERSION:            (lambda v: str(v)),
}

ARGS_FROM_STRING = _init_table(_from_string)
ARGS_TO_STRING = _init_table(_to_string)


#
# Declaration of expected arguments for each protocol request
#

# This dict contains a request table for each Solipsis protocol version
REQUESTS = {}

# 1.0 - First stable version of the Solipsis protocol
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

REQUESTS[1.0] = {
    'CLOSE'      : [ ARG_ID ],
    'CONNECT'    : NODE_ARGS + [ ARG_HOLD_TIME ],
    'HEARTBEAT'  : [ ARG_ID ],
    'HELLO'      : NODE_ARGS + [ ARG_HOLD_TIME, ARG_SEND_DETECTS ],

    'AROUND'     : REMOTE_ARGS,
    'BEST'       : NODE_ARGS,
    'DETECT'     : REMOTE_ARGS,
    'FINDNEAREST': [ ARG_ID, ARG_ADDRESS, ARG_POSITION ],
    'FOUND'      : [ ARG_REMOTE_ID, ARG_REMOTE_ADDRESS, ARG_REMOTE_POSITION ],
    'JUMPNEAR'   : [ ARG_ID, ARG_ADDRESS ],
    'NEAREST'    : [ ARG_REMOTE_ID, ARG_REMOTE_ADDRESS, ARG_REMOTE_POSITION ],
    'QUERYAROUND': [ ARG_ID, ARG_ADDRESS, ARG_POSITION, ARG_BEST_ID, ARG_BEST_DISTANCE ],
    'SEARCH'     : [ ARG_ID, ARG_CLOCKWISE ],
    'SUGGEST'    : NODE_ARGS + [ ARG_REMOTE_POSITION ],
    'UPDATE'     : NODE_ARGS,

    'META'       : [ ARG_ID, ARG_PSEUDO, ARG_ACCEPT_LANGUAGES, ARG_ACCEPT_SERVICES ],
    'QUERYMETA'  : [ ARG_ID, ARG_PSEUDO, ARG_ACCEPT_LANGUAGES, ARG_ACCEPT_SERVICES ],
    'QUERYSERVICE': [ ARG_ID, ARG_SERVICE_ID, ARG_SERVICE_ADDRESS ],
    'SERVICEINFO': [ ARG_ID, ARG_SERVICE_ID, ARG_SERVICE_ADDRESS ],
    'SERVICEDATA': [ ARG_ID, ARG_SERVICE_ID, ARG_PAYLOAD ],
}

# 1.1 - Add parameters for NAT hole punching and protocol version handling
REMOTE_ARGS = [
    ARG_ADDRESS,
    ARG_REMOTE_ADDRESS,
    ARG_REMOTE_ID,
    ARG_REMOTE_POSITION,
    ARG_REMOTE_VERSION,
    ARG_REMOTE_NEEDS_MIDDLEMAN
]

REQUESTS[1.1] = deepcopy(REQUESTS[1.0])
REQUESTS[1.1].update({
    'CONNECT'    : NODE_ARGS + [ ARG_VERSION, ARG_NEEDS_MIDDLEMAN, ARG_HOLD_TIME ],
    'HELLO'      : NODE_ARGS + [ ARG_VERSION, ARG_NEEDS_MIDDLEMAN, ARG_HOLD_TIME, ARG_SEND_DETECTS ],

    'AROUND'     : REMOTE_ARGS + [ ARG_REMOTE_AWARENESS_RADIUS ],
    'DETECT'     : REMOTE_ARGS + [ ARG_REMOTE_AWARENESS_RADIUS ],
    'FOUND'      : REMOTE_ARGS,
    'NEAREST'    : REMOTE_ARGS,

    'MIDDLEMAN'  : [ ARG_ID, ARG_REMOTE_ID, ARG_PAYLOAD ],
})


#
# Object representation of Solipsis messages
#
class Args(object):
    pass

class Message(object):
    """
    This structure is a simple representation of a Solipsis message.
    """
    def __init__(self, request = "", version=None):
        self.version = version or SAFE_VERSION
        self.request = request
        self.args = Args()

