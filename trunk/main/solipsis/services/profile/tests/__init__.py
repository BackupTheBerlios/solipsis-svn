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
"""Constants used by tests"""

import os.path
import solipsis

TEST_DIR = os.path.sep.join([os.path.dirname(solipsis.__file__), "services", "profile", "tests"])
GENERATED_DIR = os.path.join(TEST_DIR, "generated")
DATA_DIR = os.path.join(TEST_DIR, "data")
PROFILE_DIRECTORY = os.path.sep.join([TEST_DIR, "data", "profiles"])
PROFILE_TEST = "test"
PROFILE_BRUCE = "bruce"
PROFILE_UNICODE = u"zoé"
PROFILE_TATA = "tata"
PROFILE_DEMI = "demi"
PROFILE_010 = u"demi_010"
PSEUDO = "atao"
REPO = TEST_DIR

