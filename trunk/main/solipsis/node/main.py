
import os
import sys
import logging
import exceptions
from optparse import OptionParser

from twisted.internet import reactor

# Solipsis Packages
from solipsis.util.parameter import Parameters
from bootstrap import Bootstrap


def run_loop(params):
    bootstrap = Bootstrap(reactor, params)
    bootstrap.Run()


def main():
    config_file = "conf/solipsis.conf"
    usage = "usage: %prog [-dbPM] [-p <port>] [-x ... -y ...] [-e ...] [-c <port>] [-n <port>]"
    parser = OptionParser(usage)
#     parser.add_option("-h", "--help", action="help",
#                         help="display help message")
    parser.add_option("-p", "--port", type="int", dest="port",
                        help="port number for all Solipsis connections")
    parser.add_option("-b", "--robot", action="store_true", dest="bot", default=False,
                        help="bot mode (don't listen for navigator)")
    parser.add_option("-d", "--detach", action="store_true", dest="detach", default=False,
                        help="run in the background")
    parser.add_option("-x", type="long", dest="pos_x",
                        help="X start value")
    parser.add_option("-y", type="long", dest="pos_y",
                        help="Y start value")
    parser.add_option("-e", type="int", dest="expected_neighbours",
                        help="number of expected neighbours")
    parser.add_option("-c", "--control_port", type="int", dest="control_port",
                        help="control port for navigator")
    parser.add_option("-n", "--notification_port", type="int", dest="notif_port",
                        help="notification port for navigator")
    parser.add_option("-f", "--conf", dest="config_file", default=config_file,
                        help="configuration file")
    parser.add_option("-P", "--profile", action="store_true", dest="profile", default=False,
                        help="profile execution to node.prof")
#     parser.add_option("-M", "--memdebug", action="store_true", dest="memdebug", default=False,
#                         help="display periodic memory occupation statistics")
    parser.add_option("", "--pool", type="int", dest="pool", default=0,
                        help="pool of nodes")
    parser.add_option("", "--seed", action="store_true", dest="as_seed", default=False,
                        help="launch node as seed")
    params = Parameters(parser, config_file=config_file)

    if (params.detach):
        # Create background process for daemon-like operation
        import os, signal
        # Ignore SIGHUP so as not to kill the child when the parent leaves
        signal.signal(signal.SIGHUP, signal.SIG_IGN)

        # Fork and kill the parent process
        if (os.fork()):
            os._exit(0)

        # The child detaches itself from the console
        os.setsid()
        #os.chdir("/")
        os.umask(0)

        # Fork and kill the parent proces
        if (os.fork()):
            os._exit(0)

    # Create node and enter main loop
    try:
        global profile_run
        profile_run = lambda: run_loop(params)
        if (params.profile):
            # See profiler documentation:
            import hotshot
            profile = hotshot.Profile("node.prof")
            profile.run(__name__ + ".profile_run()")
            profile.close()
            #import profile
            #profile.run(__name__ + ".profile_run()", "node.prof")
        else:
            # See Psyco documentation: http://psyco.sourceforge.net/psycoguide/module-psyco.html
            import psyco
            #psyco.full()
            psyco.profile(watermark=0.005, time=120)
            profile_run()
    except Exception, e:
        raise


if __name__ == '__main__':
    main()

