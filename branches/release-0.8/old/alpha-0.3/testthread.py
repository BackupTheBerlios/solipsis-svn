import unittest
import sys
from threading import Thread, Condition, RLock
from Queue import Queue
from time import sleep

class ProducerConsumerTestCase(unittest.TestCase):
    def setUp(self):        
        self.access = Condition()
        self.count = 0
        self.consumed = 0
        self.produced = 0
        self.data = 0

    def consumer(self,n):
            
        while 1:
            self.access.acquire()
            while self.count == 0:
                #print "consumer waiting"
                self.access.wait()
            i = self.data
            self.count = 0
            self.access.notify()
            self.access.release()
            self.consumed += 1
            #print "consumed " + str(self.consumed)
            if i == n:
                break

    def producer(self, n):
    
        for i in xrange(1,n+1):
            self.access.acquire()
            while self.count == 1:
                #print "producer waiting"
                self.access.wait()
            self.data = i
            self.count = 1
            self.access.notify()
            self.access.release()
            self.produced += 1
            #print "produced " + str(self.produced)

    def testThread(self):
        n = 12
        t1 = Thread(target=self.producer, args=(n,))
        t2 = Thread(target=self.consumer, args=(n,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        assert (self.produced == n)
        assert (self.consumed == n)
        print " n= %d, produced=%d, consumed=%d\n" %(n,self.produced, self.consumed)
    

        
class ProducerThread(Thread):

    def __init__(self, queue, quota):
        Thread.__init__(self, name="Producer")
        self.queue = queue
        self.quota = quota
        
    def run(self):
        from random import random
        counter = 0
        while counter < self.quota:
            counter = counter + 1
            self.queue.put("%s.%d" % (self.getName(), counter))
            #print "Produced %s.%d" % (self.getName(), counter)
            sleep(random() * 0.001)


class ConsumerThread(Thread):

    def __init__(self, queue, count):
        Thread.__init__(self, name="Consumer")
        self.queue = queue
        self.count = count

    def run(self):
        while self.count > 0:
            self.queue.lock.acquire()
            if self.queue.empty():
                #print "consumer waiting"
                self.queue.lock.wait()
            self.queue.lock.release()
            item = self.queue.get()
            
            #print "consumed " + str(item)
            self.count = self.count - 1


class ConditionQueue(Queue):
    def __init__(self):
        Queue.__init__(self)
        self.lock = Condition()
        
    def get(self):
        return Queue.get(self, False)

    def put(self, item):
        self.lock.acquire()
        Queue.put(self, item)
        self.lock.notify()
        self.lock.release()
        
class ProducerConsumerTestCase2(unittest.TestCase):
    def testThread(self):
        NP = 3
        QL = 4
        NI = 5

        Q = ConditionQueue()
        P = []
        for i in range(NP):
            t = ProducerThread(Q, NI)
            t.setName("Producer-%d" % (i+1))
            P.append(t)
        
        C = ConsumerThread(Q, NI*NP)
        C.start()
        sleep(0.00001)
        for t in P:
            t.start()
            sleep(0.000001)
        

        for t in P:
            t.join()
        C.join()
        

if __name__ == "__main__":
  unittest.main()
  
