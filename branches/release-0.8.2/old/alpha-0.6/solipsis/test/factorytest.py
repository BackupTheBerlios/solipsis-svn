import os,sys

def main():
    from solipsis.core.event import EventFactory
    from solipsis.core.peerevent import PeerEventFactory
    from solipsis.core.controlevent import ControlEventFactory
    
    from solipsis.util.parameter import Parameters
    from solipsis.core.node import Node
    
    configFileName = searchPath + '/conf/solipsis.conf'
    params = Parameters(configFileName)
    node = Node(params)

    EventFactory.init(node)
    f1 = PeerEventFactory()
    f2 = ControlEventFactory()
    EventFactory.register(PeerEventFactory.TYPE, f1)
    EventFactory.register(ControlEventFactory.TYPE, f2)

    f3 = EventFactory.getInstance(PeerEventFactory.TYPE)
    best = f3.createBEST()
    f4 = EventFactory.getInstance(ControlEventFactory.TYPE)
    dead = f4.createDEAD(54)

    print best
    print dead
    return 0

searchPath = os.path.dirname(os.path.dirname(sys.path[0]))

if __name__ == '__main__':
    sys.path.append(searchPath)
    main()
