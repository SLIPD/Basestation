#!/usr/bin/env python

from SocketConnection import SocketConnection
from Packet import Packet
from payload import *
import threading
import sys


def quit():
    print 'Exiting...'
    global socketConnection
    socketConnection.close()
    sys.exit()

def getInput():
	while True:
		print "Enter old ID: "
		oldId = sys.stdin.readline()
		print "Enter new ID: "
		newId = sys.stdin.readline()
		'''if(data == 'quit'):
			break
		if(data == ''):
			continue
			'''	
		payload = PayloadIdentification()
		payload.initialise(int(oldId),int(newId))
		p = Packet()
		p.initialise(0,0xFF,1,0,0,payload)
		print p
		global socketConnection
		socketConnection.sendData(p.getBytes())


socketConnection = SocketConnection('', 29877)

if(not socketConnection.connectAsSender()):
    sys.exit(0)

try:
	getInput()
except:
	pass
finally:
	quit()
