#!/usr/bin/env python

import os
import os.path
import sys
import time

pool_size = 20
first_port = 5001
seed_delay = 5.0
delay = 7.0


def create_nodes(n, port, custom_args):
    prog_name = os.path.normcase('.' + os.sep + 'twistednode.py')
    args = [prog_name]
    args +=  ['-b', '-d', '-p', str(port)]
    args +=  ['-f', 'conf/seed.conf', '--pool', str(n)]
    args += custom_args
    cmdline = " ".join(args)
    print cmdline
    # Here we use subprocess for portability, but in case it doesn't exist
    # (Python < 2.4) we fall back on os.spawnv which does not allow direct
    # execution of .py files under Windows.
    try:
        import subprocess
    except ImportError:
        print "using os.spawnv..."
        os.spawnv(os.P_NOWAIT, prog_name, args)
    else:
        print "using subprocess.Popen..."
        subprocess.Popen(cmdline, shell=True)

def usage():
    print "Usage: %s <number of nodes>" % sys.argv[0]
    sys.exit(0)

def main():
    if len(sys.argv) != 2:
        usage()
    nb_nodes = int(sys.argv[1])
    i = 0
    port = first_port
    while i < nb_nodes:
        n = min(nb_nodes - i, pool_size)
        if i==0:
            create_nodes(n, port, ['--seed'])
            time.sleep(seed_delay)
        else:
            create_nodes(n, port, [])
            time.sleep(delay)
        port += n
        i += n


if __name__ == '__main__':
    if os.environ.has_key('PYTHONPATH'):
        os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':.'
    else:
        os.environ['PYTHONPATH'] = '.'

    main()
