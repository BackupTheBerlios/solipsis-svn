# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>


class DelayedCall(object):
    """
    To create a delayed call, please use a DelayedCaller instance,
    do not instantiate this class directly.
    """
    def __init__(self, caller, id_):
        self.caller = caller
        self.id_ = id_

    def Reschedule(self):
        """
        Reschedules the delayed call, i.e. restarts its countdown from
        the initial value.
        """
        self.caller.RescheduleCall(self.id_)

    def Cancel(self):
        """
        Cancel the delayed call.
        (do not call more than once)
        """
        self.caller.CancelCall(self.id_)

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
        assert len(self.calls) == 0, "delayed caller should be reset manually"
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
        Returns a DelayedCall object.
        """
        id_ = self._CallLater(_delay, _function, *args, **kargs)
        return DelayedCall(self, id_)

    def CallPeriodically(self, _period, _function, *args, **kargs):
        """
        Call a function once in a while.
        Returns a DelayedCall object.
        """
        id_ = self._CallPeriodically(_period, _function, *args, **kargs)
        return DelayedCall(self, id_)

    def CancelCall(self, id_):
        """
        Remove a call.
        """
        if id_ not in self.calls:
            return
        try:
            self.calls[id_].cancel()
        except Exception, e:
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

    def _CallLater(self, _delay, _function, *args, **kargs):
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

    def _CallPeriodically(self, _period, _function, *args, **kargs):
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
