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

from exceptions import *


class UnauthorizedRequest(Exception):
    def __init__(self, msg = ""):
        Exception.__init__(self, msg or "Unauthorized request to the node")
    pass



class ConnectionError(IOError):
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Cannot connect to Solipsis'
        IOError.__init__(self, msg)

class EventParsingError(Exception):
    """ An error occured while parsing a solipsis message"""
    def __init__(self, msg = ""):
        Exception.__init__(self, msg)

class AbstractMethodError(NotImplementedError):
    """ An abstract method has been used. """
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Error, trying to use an abstract method'
        NotImplementedError.__init__(self, msg)

class InternalError(RuntimeError):
    """ Generic solipsis exception. Program internal error, we shouldn't raise
    this exception in a production environement."""
    def __init__(self, msg = ""):
        RuntimeError.__init__(self, msg)

class ConnectorError(IOError):
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Connection aborted, please check port in not already in use'
        IOError.__init__(self, msg)

class DuplicateIdError(Exception):
    def __init__(self, id_):
        msg = "Error : duplicate ID '" + str(id_) + "'"
        Exception.__init__(self, msg)

class UnknownIdError(Exception):
    def __init__(self, id_):
        msg = "Error : unknown ID" + str(id_)
        Exception.__init__(self, msg)

class EmptyIdError(Exception):
    def __init__(self):
        msg = "Error : ID is empty"
        Exception.__init__(self, msg)

