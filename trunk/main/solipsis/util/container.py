from Queue import Queue
from threading import Condition
from geometry import Geometry

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

class GenericList(object):

    def __init__(self):

        # the list
        self.ll = []

        # comparaison function
        self.cmpFunc = None

    def insert(self, entity):
        """ insert entity in the list"""
        self.ll.insert(self.dichotomy(entity), entity)

    def __len__(self):
        return len(self.ll)

    def dichotomy(self, entity):
        """ return the index at which the element entity may be inserted using
        dichotomic scheme """

        start = 0
        end = len(self)
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

    def replace(self, entity):
        """ replace, if required, a moving entity in the list"""

        i = self.ll.index(entity)
        # boolean variables to indicate that the entity has moved, either up or down
        down, up = 0, 0
        k = 1
        # i is before i-1, i-2, ...
        while i-k <> -1 and self.cmpFunc(self.ll[i-k], self.ll[i]) > 0:
            k += 1
            down = 1

        if not down:
            # i+1, i+2... is before i
            while i+k <> len(self) and self.cmpFunc(self.ll[i], self.ll[i+k]) > 0:
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
            if i+k == len(self):
                self.ll.append(entity)
                self.ll.pop(i)
            else:
                self.ll.insert(i+k, entity)
                self.ll.pop(i)



class CcwList(GenericList):
    """ entities sorted counterclockwise"""

    def __init__(self):
        super(CcwList,self).__init__()
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

class DistList(GenericList):
    """ entities sorted by distance criteria"""

    def __init__(self):
        super(DistList,self).__init__()

        # compraison function
        self.cmpFunc = Geometry.distOrder

