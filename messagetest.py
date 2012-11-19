from payload import *
from random import *


def fakeMessage():
    current = ""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,<>/?;:|!@#%&*()-_=+'$"
    length = randint(1,100)
    for i in range(0,length):
        current += alphabet[randint(0,len(alphabet) - 1)]
    return current

def strcompare(s1,s2):
    if(len(s1) != len(s2)):
        return False
    for i in range(0,len(s1)):
        if(s1[i] != s2[i]):
            return False
    return True

tests = []
for i in range(1,1000):
    tests.append(fakeMessage())

for test in tests:
    m = PayloadMessage()
    m.initialise(test)
    m.encryptMessage()
    m.decryptMessage()
    if(strcompare(m.__str__(),"(message) = (" + test + ")")):
        print "        " + m.__str__()
        print "RETURN: (message) = (" + test + ")"
print "Tests complete"
        