class A:
    def __init__(self, id):
        self.id = id
        
    def say(self, word):
        print "a.say " + word + " with id "+ str(self.id)

class B:
    def __init__(self):
        self.a = A(12)
        
    def run(self):
        method = "say"
        var = 'hello'
        stmt = 'self.a.'+ method + '(var)'
        eval(stmt)


if __name__ == "__main__":
    b = B()
    b.run()
