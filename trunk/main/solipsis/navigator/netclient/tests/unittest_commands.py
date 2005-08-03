import unittest

from solipsis.navigator.netclient.network import Commands, SolipsisUiFactory
from twisted.internet import defer

class Dummy:

    def do_no(self, deferred):
        return "none"

    def do_one(self, deferred, arg):
        return "one: %s"% arg

    def do_two(self, deferred, first, second=None):
        return "two: %s, %s"% (first, second)

class CommandTest(unittest.TestCase):

    def setUp(self):
        self.worker = Dummy()
        self.deferred = defer.Deferred()
        self.no_cmd = Commands("no", "No argument",
                               converter=lambda : None)
        self.one_cmd = Commands("one", "One argument", "default")
        self.two_cmd = Commands("two", "Two arguments", "localhost", 80,
                                converter=lambda s: (s.split(":")[0], int(s.split(":")[1])))

    def test_convert(self):
        self.assertEquals(self.no_cmd.convert(), None)
        self.assertEquals(self.one_cmd.convert(2), ("2",))
        self.assertEquals(self.two_cmd.convert("127.0.0.1:8080"), ("127.0.0.1", 8080))

    def test_call_no(self):
        self.assertEquals(self.no_cmd.call(self.worker, self.deferred), "none")
        self.assertRaises(TypeError, self.no_cmd.call, self.worker, self.deferred, "anything")
        
    def test_call_one(self):
        self.assertEquals(self.one_cmd.call(self.worker, self.deferred), "one: default")
        self.assertEquals(self.one_cmd.call(self.worker, self.deferred, "both"), "one: both")
        self.assertRaises(TypeError, self.one_cmd.call, self.worker, self.deferred, "anything", "left_over")

    def test_call_two(self):
        self.assertEquals(self.two_cmd.call(self.worker, self.deferred), "two: localhost, 80")
        self.assertEquals(self.two_cmd.call(self.worker, self.deferred, "youpi"), "two: youpi, None")
        self.assertEquals(self.two_cmd.call(self.worker, self.deferred, "youpi", 4), "two: youpi, 4")
        converted = self.two_cmd.convert("address:23")
        self.assertEquals(self.two_cmd.call(self.worker, self.deferred, *converted), "two: address, 23")
        self.assertEquals(self.two_cmd.call(self.worker, self.deferred, "saturne:25", convert=True), "two: saturne, 25")
        
if __name__ == "__main__":
    unittest.main()
