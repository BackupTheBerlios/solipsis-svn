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

import sys
from optparse import OptionParser

# Solipsis Packages
from solipsis.util.parameter import Parameters
from app import NavigatorApp

def main():
    config_file = "conf/solipsis.conf"
    usage = "usage: %prog [-f <config file>]"
    parser = OptionParser(usage)
    parser.add_option("-f", "--file", dest="config_file", default=config_file,
                        help="configuration file")
    params = Parameters(parser, config_file=config_file)

    application = NavigatorApp(redirect=False, parameters=params)
    application.MainLoop()
    sys.exit(0)

if __name__ == "__main__":
    main()
