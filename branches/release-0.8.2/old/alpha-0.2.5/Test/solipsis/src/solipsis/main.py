import solipsis.main
from solipsis.engine.startup import Node
from solipsis.navigator.ihm import Ihm
import ConfigParser


def testConfig():
    cp = ConfigParser.ConfigParser()
    cp.read("solip.conf")
    t_false = cp.getboolean("general","t_false");
    t_true = cp.getboolean("general","t_true");
    t_long = cp.get("general","t_long")
    t_int = cp.get("general","t_int")

    print "t_false: %s\n" % t_false
    print "t_true: %s\n" % t_true
    
    print "t_long: %s\n" % t_long
    print "t_int: %s\n" % t_int

    print "int(t_int): %d" % int(eval(t_int))
    print "long(t_long): %s\n" % long(eval(t_long))
    if ( t_false ):
        print "t_false is true\n"
    else:
        print "t_false is false\n"
    if ( t_true ):
        print "t_true is true\n"
    else:
        print "t_true is false\n"
    

if __name__ == '__main__':
    mynode = Node()
    mynode.log()
    myihm = Ihm()
    myihm.log()
    testConfig();
