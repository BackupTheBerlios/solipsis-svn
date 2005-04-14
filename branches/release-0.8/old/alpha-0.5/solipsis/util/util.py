import math
from Queue import Queue
from threading import Condition
from solipsis.engine.entity import Position

class NotificationQueue(Queue):
    """ A queue class that notifies waiting threads when the queue is available for
    reading."""
    def __init__(self):
        """ Constructor."""
        Queue.__init__(self)
        self.lock = Condition()
        
    def get(self):
        """ Get an item from the queue. This method is thread-safe.
        Method must be called on a non-empty queue.
        Return : the first item from the queue
        Raises: a EmptyQueue exeception
        """
        return Queue.get(self, False)

    def put(self, item):
        """ Add a new item to the queue. This method is thread-safe.
        Threads that are waiting for get an item are notified.
        item: new item to add to the queue.
        Return : None
        """
        self.lock.acquire()
        Queue.put(self, item)
        self.lock.notify()
        self.lock.release()

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()

    def wait(self):
        self.lock.wait()

class Geometry:
    # size should be initialized before class is used
    SIZE = 0
    
    def distance(p1, p2):
        """ compute euclidean distance for the minimal geodesic between two
        positions p1 and p2
        Static method.
        """
        rp1 = Geometry.relativePosition(p1, p2)
        return long ( math.hypot( rp1.getPosX()-p2.getPosX(),
                                  rp1.getPosY()-p2.getPosY() ) )
    
    def relativePosition(pos, ref):
        """ Return the relative position of pos (relative to ref)
        Static method.
        Internal method only used by Geometry module, since the relative position
        can be outside the coordinate system
        E.g. If SIZE = 20 (coordinates from (-10,-10) to (10,10)),
        the point (9,1) is close to point (-9, 1): the distance between
        these points is 2.
        relative position of (9,1) is then (-11,1)
        """

        result = Position(pos.getPosX(), pos.getPosY())

        #-----Step 1: x-axis

        if pos.getPosX() > ref.getPosX():
            if pos.getPosX() - ref.getPosX() > Geometry.SIZE/2:
                result.setPosX(pos.getPosX() - Geometry.SIZE)
        else:
            if ref.getPosX() - pos.getPosX() > Geometry.SIZE/2:
                result.setPosX(pos.getPosX() + Geometry.SIZE)

        #-----Step 2: y-axis

        if pos.getPosY() > ref.getPosY():
            if pos.getPosY() - ref.getPosY() > Geometry.SIZE/2:
                result.setPosY(pos.getPosY() - Geometry.SIZE)
        else:
            if ref.getPosY() - pos.getPosY() > Geometry.SIZE/2:
                result.setPosY(pos.getPosY() + Geometry.SIZE)

        return result


    def localPosition(peerPosition, origin):
        """ Return the new coordinate of a point, using a new origin.
        Used to compute the coordinate of a peer in the coordinate system centered
        around the node: in this system the node has coordinate [0,0]
        peerPosition: old coordinate of point
        origin: new origin for the new coordinate system """
        # compute relative position of these two points
        relativePeerPosition = Geometry.relativePosition(peerPosition, origin)
        
        return Position(relativePeerPosition.getPosX() - origin.getPosX(),
                relativePeerPosition.getPosY() - origin.getPosY())
    
    def inHalfPlane(p1, p2, pos):
        """ compute if pos belongs to half-plane delimited by (p1, p2)
        p2 is the central point for ccw
        return boolean TRUE if pos belongs to half-plane"""
        rp1  = Geometry.relativePosition(p1,p2)
        rpos = Geometry.relativePosition(pos, p2)
        return (rpos.getPosX()-rp1.getPosX())*(rp1.getPosY()-p2.getPosY()) + \
               (rpos.getPosY()-rp1.getPosY())*(p2.getPosX()-rp1.getPosX()) > 0
            
    def ccwOrder(x, y):
        """ return TRUE if entity y is before entity x in ccw order relation
        to position of the node (coordinate [0,0] using local position"""
  
        # take the p-relative position of x and y
        xx = x.localPosition
        yy = y.localPosition

        # verify that they lie in the same half-plane (up or down to pos)
        upX = xx.getPosY() <= 0
        upY = yy.getPosY() <= 0

        if upX <> upY:
            # they do not lie to the same half-plane, y is before x if y is up
            result = upY
        else:
            # they lie in the same plane, compute the determinant and check the sign
            result = not Geometry.inHalfPlane(xx, Position(0,0), yy)
    
        return result    

    def distOrder(x, y):
        """ return TRUE if entity y is closer to the node than entity x
        Node is at coordinate [0,0]
        """

        xx = x.localPosition
        yy = y.localPosition
        
        return ( Geometry.distance(yy, Position(0,0)) <
                 Geometry.distance(xx, Position(0,0)) )

    distance = staticmethod(distance)
    relativePosition = staticmethod(relativePosition)
    localPosition = staticmethod(localPosition)
    inHalfPlane = staticmethod(inHalfPlane)
    ccwOrder = staticmethod(ccwOrder)
    distOrder = staticmethod(distOrder)
    
class GenericList:

    def insert(self, entity):
        """ insert entity in the list"""

        self.ll.insert(self.dichotomy(entity), entity)
        self.length += 1
        
    def __len__(self):
        return self.length
    
    def dichotomy(self, entity):
        """ return the index at which the element entity may be inserted using
        dichotomic scheme """

        start = 0
        end = self.length
        while start < end :
            i = (start + end)>>1 # (start + end)/2
            pivot = self.ll[i]
            if self.cmpFunc(pivot, entity) > 0: # pivot > entity
                end = i
            else:
                start = i+1

        return start

    def delete(self, entity):
        """ delete entity from the list"""

        if self.ll.count(entity) <> 0:
            self.ll.remove(entity)
            self.length -= 1

    def update(self, p):
        """ update list when self.p moves"""
        self.ll.sort(self.cmpFunc)

            
    def replace(self, entity):
        """ replace, if required, a moving entity in the list"""

        i = self.ll.index(entity)
        down, up = 0, 0 # boolean variables to indicate that the entity has moved, either up or down
        k = 1
        while i-k <> -1 and self.cmpFunc(self.ll[i-k], self.ll[i]) > 0: # i is before i-1, i-2, ...
            k += 1
            down = 1
           
        if not down:
            while i+k <> self.length and self.cmpFunc(self.ll[i], self.ll[i+k]) > 0: # i+1, i+2... is before i
                k += 1
                up = 1
                
        # replace the entity if its position was not well
        if down:
            if i-k == -1:
                self.ll.pop(i)
                self.ll.insert(0,entity)
            else:
                self.ll.pop(i)
                self.ll.insert(i-k+1, entity)
        elif up:
            if i+k == self.length:
                self.ll.append(entity)
                self.ll.pop(i)
            else:
                self.ll.insert(i+k, entity)
                self.ll.pop(i)
                
    

class CcwList(GenericList):
    """ entities sorted counterclockwise"""

    def __init__(self):

        # the list
        self.ll = []

        # length of the list
        self.length = 0

        # comparaison function
        self.cmpFunc = Geometry.ccwOrder

    def filterList(self, sector):
        """ create a list from entities in ll and in sector"""

        i = self.dichotomy(sector.startEnt) 
        j = self.dichotomy(sector.endEnt)
        
        if i <= j :
            result = self.ll[i:j]
        else:
            result = self.ll[i:]+self.ll[:j]
            
        return result

    def checkGlobalConnectivity(self):
        """ check if global connectivity is ensured

        return a list of pair of entities not respecting property"""
        result = []

        # three or more entities,
        if self.length > 3:
	  for index in range(self.length-1) :
	    ent = self.ll[index]
	    next_ent = self.ll[ (index+1) % self.length ]
	    if not inHalfPlane(ent.local_position, Position(0,0), next_ent.local_position) :
	      result.append( [ ent, next_ent ] )
	
	return result      
	

class DistList(GenericList):
    """ entities sorted by distance criteria"""
    
    def __init__(self):

        # the list
        self.ll = []

        # length of the list
        self.length = 0

        # compraison function
        self.cmpFunc = Geometry.distOrder

    def closer_to_d(self,d):
      """ return number of entities closer than distance d"""  
      result = 0
      while result < self.length and distance( self.ll[result].local_position,
                                               Position(0,0) ) < d :
          result += 1

      return result
    
