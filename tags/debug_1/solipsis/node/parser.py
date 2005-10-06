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
import logging

from solipsis.util.compat import set, safe_str, safe_unicode
from solipsis.util.exception import *
from protocol import *

def banner(version=None):
    return BANNER + str(version)

class Parser(object):
    """
    This class parses and builds Solipsis messages.
    """
    request_syntax = re.compile(r'^\s*(\w+)\s+SOLIPSIS/(\d+\.\d+)\s*$')
    argument_syntax = re.compile(r'^\s*([-\w]+)\s*:\s*(.*?)\s*$')
    line_separator = "\r\n"

    def __init__(self):
        self.logger = logging.getLogger('root')

    def StripMessage(self, message, version=None):
        """
        Strip unnecessary parameters from message.
        """
        version = version or message.version
        try:
            _req = REQUESTS[version][message.request]
        except KeyError:
            raise EventParsingError("Unknown request '%s' in version '%s'" % (message.request, str(version)))
        required_args = set([ATTRIBUTE_NAMES[arg_id] for arg_id in _req])
        args = message.args
        for k in set(args.__dict__) - required_args:
            delattr(args, k)

    def BuildMessage(self, message, version=None):
        """
        Build protocol data from message.
        """
        lines = []
        args = message.args.__dict__
        payload = ""
        version = min(version or message.version, VERSION)

        # 0. Remove unnecessary fields
        self.StripMessage(message, version)
        # 1. Request and protocol version
        first_line = message.request + " " + banner(version)
        lines.append(first_line)
#         print ">", first_line
        # 2. Request arguments
        for k, v in args.iteritems():
            arg_id = ATTRIBUTE_NAMES.get_reverse(k)
            if arg_id == ARG_PAYLOAD:
                payload = safe_str(v, CHARSET)
            else:
                lines.append('%s: %s' % (PROTOCOL_STRINGS[arg_id], ARGS_TO_STRING[arg_id](v)))
        # 3. End of message (double CR-LF)
        data = "\r\n".join(lines) + "\r\n\r\n" + payload
        # In debug mode, parse our own message to check it is well-formed
        assert self.ParseMessage(data, parse_only=True), "Bad generated message: " + data
        return data

    def ParseMessage(self, data, parse_only=False):
        """
        Parse and extract message from protocol data.
        """
        # Parse raw data to construct message (strip empty lines)
        lines = data.split(self.line_separator)
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

        # Version check
        if version > VERSION:
            raise EventParsingError("Unexpected protocol version: %s" % str(version))
        elif version < VERSION:
            self.logger.info("Received message from older protocol version: %s" % str(version))
        # Request check
        if not request in REQUESTS[version]:
            raise EventParsingError("Unknown request: " + request)

        # Get args for this request
        mandatory_args = REQUESTS[version][request]
        missing_args = set(mandatory_args)
        args = {}

        # Now let's parse each parameter line in turn
        for nb_line in xrange(1, len(lines)):
            line = lines[nb_line]
            if len(line) == 0:
                break
            # Get arg name and arg value
            t = line.split(':', 1)
            if len(t) != 2:
                raise EventParsingError("Invalid message syntax:\r\n" + data)
            name = t[0].strip()
            value = t[1].strip()

            # Each arg has its own syntax-checking regex
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
            try:
                missing_args.remove(arg_id)
            except KeyError:
                self.logger.debug("Unexpected argument '%s' in message '%s'" % (name, request))

        # Is there a payload ?
        if nb_line + 1 < len(lines):
            payload = self.line_separator.join(lines[nb_line+1:])
            if payload:
                if ARG_PAYLOAD in missing_args:
                    missing_args.remove(ARG_PAYLOAD)
                else:
                    self.logger.debug("Optional payload in message '%s'" % request)
                # Note: we don't try to convert the payload to unicode when
                # receiving, because it could really be a binary string.
                # This makes the message handling slightly asymetric.
                args[ARG_PAYLOAD] = payload

        # Check that all required fields have been encountered
        if missing_args:
            raise EventParsingError("Missing arguments (%s) in message '%s'"
                    % (",".join([PROTOCOL_STRINGS[arg] for arg in missing_args]), request))

        # Everything's ok
        if not parse_only:
            message = Message()
            message.request = request
            message.version = version
            for arg_id, value in args.iteritems():
                setattr(message.args, ATTRIBUTE_NAMES[arg_id], value)
            return message
        else:
            return True


def _test():
    data = ("HEARTBEAT SOLIPSIS/1.0\r\n" +
            "Id: 192.168.0.1\r\n" +
            "Position: 455464, 78785425, 0\r\n" +
            "Clockwise: -1\r\n" +
            "\r\ntoto")
    parser = Parser()
    message = parser.ParseMessage(data)
    print message.request
    print message.args.__dict__
    data = parser.BuildMessage(message)
    print data
    message = parser.ParseMessage(data)
    print message.args.__dict__

if __name__ == '__main__':
    _test()
