# pylint: disable-msg=W0131
# Missing docstring
#
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
"""defines functions to display message in navigator. These functions
do not do anything if no navigator is defined (in tests for instance)"""

__revision__ = "$Id: __init__.py 865 2005-09-30 08:28:36Z emb $"

from solipsis.services.profile.tools.prefs import get_prefs

def _display(msg, msg_type, title="Solipsis Profile", error=None):
    from solipsis.services.profile.plugin import Plugin
    service_api = Plugin.service_api
    if service_api != None:
        if msg_type == "ERR":
            from traceback import extract_stack
            service_api.display_error(msg, title,
                                      error=error,
                                      trace=extract_stack()[:-2])
        elif msg_type == "WARN":
            service_api.display_warning(msg, title)
        elif msg_type == "MSG":
            service_api.display_message(msg, title)
        elif msg_type == "STATE":
            service_api.display_status(msg)
        else:
            print "message type %s not valid"
#     else:
#         print "MSG: " + msg
#         if not error is None:
#             print "ERR: ", error
#             import traceback
#             traceback.print_exc()
    
def display_error(msg, title="Profile Error", error=None, trace=None):
    _display(msg, "ERR", title, error)

def display_warning(msg, title="Profile Warning"):
    _display(msg, "WARN", title)

def display_message(msg, title="Profile Information"):
    _display(msg, "MSG", title)
    
def display_status(msg):
    _display(msg, "STATE")
    
def log(*args):
    if get_prefs("log"):
        formatted = []
        for arg in args:
            if isinstance(arg, unicode):
                formatted.append(arg.encode(get_prefs("encoding")))
            else:
                formatted.append(str(arg))
        # log
        print ' '.join(formatted)
