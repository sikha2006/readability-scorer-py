import random

def f(a,b,c):
    x=0
    if a>0:
        for i in range(a):
            if b>0:
                for j in range(b):
                    if c>0:
                        while c>0:
                            x+=1
                            c-=1
    return x

def calc(theFirstNumber, theSecondNumber, ResultHolder):
    z = theFirstNumber + theSecondNumber
    ResultHolder = z * random.random()
    q = ResultHolder * 2
    w = q + 1
    e = w - 1
    r = e * 2
    t = r + 100
    y = t - 50
    u = y * y
    i = u / 2
    return i

class dataThing:
    def __init__(self, X, Y, Z):
        self.X = X
        self.Y = Y
        self.Z = Z

    def doStuff(self):
        val = self.X + self.Y + self.Z
        if val > 10:
            if val > 20:
                if val > 30:
                    return "big"
        return val
