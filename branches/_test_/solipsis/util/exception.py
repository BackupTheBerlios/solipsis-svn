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



class EventParsingError(Exception):
    """
    Triggered when a bad Solipsis message is encountered.
    TODO: change class name ;-)
    """
    def __init__(self, msg = ""):
        Exception.__init__(self, msg)

class DuplicateIdError(Exception):
    """
    Triggered when trying to add two peers with the same ID.
    """
    def __init__(self, id_):
        msg = "Error : duplicate ID '" + str(id_) + "'"
        Exception.__init__(self, msg)

class UnknownIdError(Exception):
    """
    Triggered when trying to do stuff with an unknown peer ID.
    """
    def __init__(self, id_):
        msg = "Error : unknown ID" + str(id_)
        Exception.__init__(self, msg)

class UnauthorizedRequest(Exception):
    """
    Triggered when a remote controller does not have a proper connection ID.
    """
    def __init__(self, msg = ""):
        Exception.__init__(self, msg or "Unauthorized request to the node")

class BadInstall(Exception):
    """
    Triggered when there is something wrong with the local Solipsis install
    (e.g. a vital file is missing).
    """
    def __init__(self, msg = ""):
        Exception.__init__(self, msg or "Your Solipsis installed seems bad or corrupted.")
