#!/usr/bin/env python

from SerialConnection import SerialConnection
from SocketConnection import SocketConnection
from Packet import Packet
import threading
import time
import sys

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
        time.sleep(0.1)
        
def getInput():
	print "Waiting for input socket connection"
	listeningSocket = SocketConnection('',29877)
	print "Input connection created"
	if listeningSocket.connectAsReceiver():
		print "Connected as receiver"
		while True:
			data = listeningSocket.receiveData(32)
			print "Writing: " + data.encode('hex_codec')
			serial.write(data)
	else:
		print "NO LISTENING CONNECTION"


databuffer = []

socketConnection = SocketConnection()

if(socketConnection.connectAsSender()):
	threading.Thread(target = sendLoop).start()
	threading.Thread(target = getInput).start()
	
	print 'Thread started'
	
	serial = SerialConnection()
	serial.connect("/dev/ttyUSB0")
	
	serial.removeInitialNulls()
	
	print "NULLS REMOVED"
	
	while True:
		data = serial.read(32)
		packet = Packet(data)
		print data.encode('hex_codec')
		if(not packet.isMessage()):
			databuffer.append(data)
		print packet
	
	
	serial.close()
	
	quit()
