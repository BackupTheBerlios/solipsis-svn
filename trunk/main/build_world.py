#!/usr/bin/env python

import os, sys
import time

pool_size = 20
first_port = 5001
seed_delay = 5.0
delay = 6.0


def create_nodes(n, port, custom_args):
    prog_name = './twistednode.sh'
    args = [prog_name]
    args +=  ['-b', '-d', '-p', str(port)]
    args +=  ['-f', 'conf/seed.conf', '--pool', str(n)]
    args += custom_args
    print " ".join(args)
    pid = os.spawnvpe(os.P_NOWAIT, prog_name, args, os.environ)
    return pid

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
