import wx
from testwximport2 import B

class A:
    def __init__(self):
        self.id = wx.NewId()
        self.B = B()

    def hello(self):
        print 'a.id= %s - b.id=%s' %(self.id, self.B.id)
        
if __name__ == "__main__":
    a = A()
    a.hello()
