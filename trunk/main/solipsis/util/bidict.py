"""
A bi-directional dictionary.
It functions like a normal dictionary, except that it also
builds a reverse mapping from values to keys.

To access the reverse mapping, just use the get_reverse() method
instead of the traditionnal get() method.

Warning: only simple access methods are implemented.
Don't try to use other methods than d[] = '...' to modify the
dictionary, otherwise the reverse mapping will be out of sync.

"""

class bidict(dict):
    def __init__(self):
        super(bidict, self).__init__()
        self._rev = {}

    def __setitem__(self, key, value):
        super(bidict, self).__setitem__(key, value)
        self._rev[value] = key

    def __delitem__(self, key):
        value = self[key]
        super(bidict, self).__delitem__(key)
        del self._rev[value]

    def get_reverse(self, value, default=None):
        """ Get the key corresponding to the given value. """
        return self._rev.get(key, default)

    def reversed(self):
        return self._rev


