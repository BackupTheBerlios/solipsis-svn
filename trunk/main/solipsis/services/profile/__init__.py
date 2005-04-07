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
"""Plugin profile: allow users to define a set of personal information
and exchange it with other peers"""

import os.path

ENCODING = "ISO-8859-1"
PROFILE_DIR = os.path.join(os.path.expanduser("~/"), ".solipsis/profiles")
PROFILE_FILE = ".default.prf"

if not os.path.isdir(PROFILE_DIR):
    print "creating conf directory %s"% PROFILE_DIR
    os.makedirs(PROFILE_DIR)
