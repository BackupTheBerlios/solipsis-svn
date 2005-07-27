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
"""base entry point with common options (does not include URL
loader. Options may be added with new entries in OPTIONS"""

from optparse import OptionParser
from solipsis.util.parameter import Parameters

DEFAULT_FILE = "conf/solipsis.conf"
USAGE = "usage: %prog [-f <config file>] [--url <url>]"
OPTIONS = [
    {"shortcut": "-f", 
     "command": "--file", 
     "dest": "config_file",
     "action": "store",
     "default": DEFAULT_FILE,
     "help": "configuration file"},
    {"shortcut": "-M", 
     "command": "--memdebug",
     "dest": "memdebug",
     "action": "store_true",
     "default": False,
     "help": "dump memory occupation statistics"},
    {"shortcut": "",
     "command": "--url",
     "dest": "url_jump",
     "action": "store",
     "default": "",
     "help": "URL to jump to"},
    ]

def build_params():
    """construct and returns config, base on optparse"""
    parser = OptionParser(USAGE)
    for option in OPTIONS:
        parser.add_option(option["shortcut"], 
                          option["command"], 
                          dest=option["dest"], 
                          action=option["action"], 
                          default=option["default"],
                          help=option["help"])
    return Parameters(parser, config_file=DEFAULT_FILE)
