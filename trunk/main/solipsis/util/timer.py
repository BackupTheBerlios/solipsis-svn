
import time
import math


class AutoTimer(object):
    """ This class is a simple timer. """

    def __init__(self):
        self.Reset()

    def Read(self):
        """ Returns latest tick as well as total elapsed time. """
        t = time.time()
        tick = t - self.last
        elapsed = t - self.first
        self.last = t
        return (tick, elapsed)

    def Reset(self):
        """ Sets the timer to the current time. """
        self.last = self.first = time.time()


class LoopTimer(object):
    """ This class implements a wrapping timer. Define its loop period
    and it will return its position inside the loop (between 0.0 and 1.0). """

    def __init__(self, loop):
        self.loop = loop
        self.Reset()

    def Read(self):
        """ Returns position inside the loop, both from latest tick and from last rest. """
        t = time.time()
        tick = math.fmod(t - self.last, self.loop)
        elapsed = math.fmod(t - self.first, self.loop)
        self.last = t
        # Conserve precision by storing the nearest value
        self.first = t - elapsed
        return (tick / self.loop, elapsed / self.loop)

    def Reset(self):
        """ Sets the timer to the current time. """
        self.last = self.first = time.time()


def TriangleFunc(bottom=0.0, top=1.0):
    def func(x):
        x = 2.0 * math.modf(x)[0]
        if x < 1.0:
            return bottom * (1.0 - x) + top * x
        else:
            return bottom * (x - 1.0) + top * (2.0 - x)
    return func

def SawtoothFunc(begin=0.0, end=1.0):
    def func(x):
        x = math.modf(x)[0]
        return begin * (1.0 - x) + end * x
    return func

def ExpFunc(begin=0.0, end=1.0, limit=0.01):
    mult = math.log(limit)
    def func(x):
        return 1.0 - math.exp(mult * x)
    return func


class Looper(object):
    """ A Looper allows you to build a loop of values.
    Please use one of the derived classes:
    TriangleLooper, SawtoothLooper. """

    def __init__(self, loop, *args, **kargs):
        assert self.func_factory is not None
        self.func = type(self).func_factory(**kargs)
        self.timer = LoopTimer(loop)

    def Read(self):
        (tick, elapsed) = self.timer.Read()
        return self.func(elapsed)

    def Reset(self):
        self.timer.Reset()

class TriangleLooper(Looper):
    """ TriangleLooper: loops according to a triangle curve. """
    func_factory = staticmethod(TriangleFunc)

class SawtoothLooper(Looper):
    """ SawtoothLooper: loops according to a sawtooth curve. """
    func_factory = staticmethod(SawtoothFunc)


class Evolver(object):
    """ An Evolver allows to gradually evolve a value from
    a beginning value and an end value.
    Please use one of the derived classes :
    LinearEvolver, ExpEvolver. """

    def __init__(self, duration, begin=0.0, end=1.0, **kargs):
        assert self.func_factory is not None
        self.duration = duration
        self.func = type(self).func_factory(**kargs)
        self.timer = AutoTimer()
        self.Terminate()
#         self.Reset(begin, end)

    def Read(self):
        (tick, elapsed) = self.timer.Read()
        if elapsed > self.duration:
            self.finished = True
            return self.end
        else:
            r = self.func(elapsed / self.duration)
            return self.begin * (1.0 - r) + self.end * r

    def Reset(self, begin=None, end=None):
        if begin is not None:
            self.begin = float(begin)
        if end is not None:
            self.end = float(end)
        self.finished = False
        self.timer.Reset()

    def Terminate(self):
        self.finished = True

    def Finished(self):
        return self.finished


class LinearEvolver(Evolver):
    func_factory = staticmethod(SawtoothFunc)

class ExpEvolver(Evolver):
    func_factory = staticmethod(ExpFunc)

