#!/usr/bin/env python

from SerialConnection import SerialConnection
from SocketConnection import SocketConnection
import threading
import time


def quit():
    print 'Exiting...'
    global socketConnection
    socketConnection.close()
    sys.exit()

def sendLoop():
    while(True):
    	global databuffer
        while(len(databuffer) > 0):
            currentMsg = databuffer.pop(0)
            global socketConnection
            socketConnection.sendData(currentMsg)
        time.sleep(1)
        
def getInput():
	while True:
		device = raw_input()
		data = raw_input()
		serial.write(chr(int(device)) + data)

databuffer = []

socketConnection = SocketConnection()

if(not socketConnection.connect()):
    sys.exit(0)

threading.Thread(target = sendLoop).start()
threading.Thread(target = getInput).start()

databuffer.append('Thread started')
print 'Thread started'

serial = SerialConnection()
serial.connect("/dev/ttyUSB0",9600)

while True:
	data = serial.readline()
	databuffer.append(data)
	print data,


serial.close()

quit()
