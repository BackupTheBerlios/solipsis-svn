
import sys
from optparse import OptionParser

# Solipsis Packages
from solipsis.util.parameter import Parameters
from app import NavigatorApp

def main():
    config_file = "conf/solipsis.conf"
    usage = "usage: %prog [-c <port>] [-n <port>]"
    parser = OptionParser(usage)
    parser.add_option("-c", "--control_port", type="int", dest="control_port",
                        help="control port for navigator")
    parser.add_option("-n", "--notification_port", type="int", dest="notif_port",
                        help="notification port for navigator")
    parser.add_option("-f", "--file", dest="config_file", default=config_file,
                        help="configuration file" )
    params = Parameters(parser, config_file=config_file)

#     try:
# #         import psyco
# #         psyco.profile()
#     except:
#         print "Psyco is not installed on your machine. \n"
#         print "If you want to speed up this program, consider installing Psyco (http://psyco.sourceforge.net/)."

    application = NavigatorApp(parameters=params)
    application.MainLoop()
    sys.exit(0)

if __name__ == "__main__":
    main()
