#!/usr/bin/env python

import os, sys
from solipsis.util.parameter import Parameters
from solipsis.node.seed import Seed

def create_seed(port, x, y):
    prog_name = './twistednode.sh'
    args = [prog_name]
    args +=  ['--seed', '-b', '-p', str(port)]
    args +=  ['-x', str(x), '-y', str(y), '-f', 'conf/seed.conf']
    args += sys.argv[1:]
    print " ".join(args)
    nodePID = os.spawnvpe(os.P_NOWAIT, prog_name, args, os.environ)

def main():
    name = 'conf/seed.met'
    try:
        # read file and close
        f = file(name)
    except:
        sys.stderr.write("Error - cannot read file: %s" % name)
        sys.exit(1)

    for line in f:
        p = line.find('#')
        if p >= 0:
            line = line[:p]
        if line.split():
            port, x, y = line.split()
            create_seed(port, x, y)


if __name__ == '__main__':
    if os.environ.has_key('PYTHONPATH'):
        os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':.'
    else:
        os.environ['PYTHONPATH'] = '.'

    main()
