import startup
import ConfigParser

class Node:
    def __init__(self):
        self.myvar = 1
        try:
            cp = ConfigParser.ConfigParser()
            cp.read("conf/solipsis.conf");
            e = cp.get("node", "host")
            print "host %s\n" % e 

        except:
            print "exception\n"
            raise
    def log(self):
        print "hello from node\n"
