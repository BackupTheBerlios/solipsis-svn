from solipsis.engine.startup import Node

class Ihm:
    def __init__(self):
        self.str = "test string in ihm"

    def log(self):
        print self.str
        n = Node()
        n.log();

