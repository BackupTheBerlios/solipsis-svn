
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

    application = NavigatorApp(parameters=params)
    application.MainLoop()
    sys.exit(0)

if __name__ == "__main__":
    main()
