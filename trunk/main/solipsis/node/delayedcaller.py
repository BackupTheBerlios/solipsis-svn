

class DelayedCaller(object):
    """
    This is a delayed caller. It is able to register, reschedule and
    cancel delayed calls.
    """
    def __init__(self, reactor):
        """
        Initialize with Twisted reactor.
        """
        self.reactor = reactor
        self.calls = {}
        self.delays = {}
        self.count = 0

    def __del__(self):
        self.Reset()

    def Reset(self):
        """
        Cancel all pending calls.
        """
        for id_, delayed in self.calls.iteritems():
            try:
                delayed.cancel()
            except Exception, e:
                # This should never happen...
                print "Reset call:", id_, str(e)
        # Important: we must not create a new dict
        # (see CallLater below)
        self.calls.clear()
        self.delays.clear()

    def CallLater(self, _delay, _function, *args, **kargs):
        """
        Call a function later.
        Returns an id used for operations on this call.
        """
        return self._CallLater(None, _delay, _function, *args, **kargs)

    def CallLaterWithId(self, _id, _delay, _function, *args, **kargs):
        """
        Same as CallLater, but with a chosen id.
        """
        self._CallLater(_id, _delay, _function, *args, **kargs)

    def CallPeriodically(self, _period, _function, *args, **kargs):
        """
        Call a function once in a while.
        Returns an id used for operations on this call.
        """
        return self._CallPeriodically(None, _period, _function, *args, **kargs)

    def CallPeriodicallyWithId(self, _id, _period, _function, *args, **kargs):
        """
        Same as CallPeriodically, but with a chosen id.
        """
        self._CallPeriodically(_id, _period, _function, *args, **kargs)

    def CancelCall(self, id_):
        """
        Remove a call.
        """
        try:
            self.calls[id_].cancel()
        except:
            # This should never happen...
            print "CancelCall:", id_, str(e)
        self._RemoveCall(id_)

    def RescheduleCall(self, id_):
        """
        Remove a call.
        """
        self.calls[id_].reset(self.delays[id_])

    def _RemoveCall(self, id_):
        """
        Remove a call.
        """
        del self.calls[id_]
        del self.delays[id_]

    def _NewId(self):
        self.count += 1
        return "_%d" % self.count

    def _CallLater(self, _id, _delay, _function, *args, **kargs):
        if _id is None:
            _id = self._NewId()

        # This class defines a callable that will remove itself
        # from the list of delayed calls
        class Fun:
            def __call__(self):
                del self.calls[_id]
                del self.delays[_id]
                _function(*args, **kargs)

        # We first register the callable, then give it the
        # necessary parameters to remove itself...
        fun = Fun()
        delayed = self.reactor.callLater(_delay, fun)
        self.calls[_id] = delayed
        self.delays[_id] = _delay

        fun.calls = self.calls
        fun.delays = self.delays
        return _id

    def _CallPeriodically(self, _id, _period, _function, *args, **kargs):
        if _id is None:
            _id = self._NewId()

        # This class defines a callable that will reschedule itself
        # each time it is called
        class Fun:
            def __call__(self):
                assert _id in self.calls, "delayed called but we are not in caller anymore!"
                # We must update the internal state first, since _function may
                # reschedule or cancel the call, or even destroy the DelayedCaller
                self.calls[_id] = self.reactor.callLater(_period, self)
                _function(*args, **kargs)

        # We first register the callable, then give it the
        # necessary parameters to reschedule itself...
        fun = Fun()
        delayed = self.reactor.callLater(_period, fun)
        self.calls[_id] = delayed
        self.delays[_id] = _period

        fun.reactor = self.reactor
        fun.calls = self.calls
        return _id

