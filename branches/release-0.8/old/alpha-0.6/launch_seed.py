#!/usr/bin/env python

import os
from solipsis.util.parameter import Parameters
from solipsis.core.seed import Seed

def createNode(port, x, y):
    #args = ['./runseed.sh', 'solipsis/core/startSeed.py']
    args = ['./runseed.sh']
    args +=  ['-b', '-p', str(port)]
    args +=  ['-x', str(x), '-y', str(y), '-f', 'conf/seed.conf']
    print args
    nodePID = os.spawnvpe(os.P_NOWAIT, './runseed.sh', args, os.environ)
    os.system

def main():
    try:
        # read file and close
        name = 'conf/seed.met'
        f = file(name, 'r')
        list = f.readlines()
        f.close()
    except:
        sys.stderr.write("Error - cannot read file:" + name)
        sys.exit(0)

    for line in list:
        if line.strip():
            port, x, y = line.split()
            #print 'port %s x %s' % (port,x)
            createNode(port, x, y)


if os.environ.has_key('PYTHONPATH'):
    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':.'
else:
    os.environ['PYTHONPATH'] = '.'


if __name__ == '__main__':
    main()
