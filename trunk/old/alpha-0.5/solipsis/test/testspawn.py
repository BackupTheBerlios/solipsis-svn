import os

nodePID = os.spawnlpe(os.P_WAIT, 'python', 'python',
                                   'solipsis/engine/startup.py',os.environ)

print "nodePID=" + str(nodePID)

