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

import os
import os.path
import solipsis

from solipsis.navigator.main import build_params
from solipsis.navigator.netclient.app import NavigatorApp
from solipsis.navigator.netclient.tests import LOCAL_PORT

if __name__ == "__main__":
    # app needs logging dir and state too
    if not os.path.exists("log"):
        os.mkdir("log")
    if not os.path.exists("state"):
        os.mkdir("state")
    # get conf file
    solipsis_path = os.path.abspath(os.path.dirname(solipsis.__file__))
    conf_file = os.path.normpath(os.sep.join([solipsis_path, "..",
                                              "conf", "solipsis.conf"]))
    # launch application
    params = build_params(conf_file)
    params.testing = True
    params.local_port = LOCAL_PORT
    navigator = NavigatorApp(params=params)
