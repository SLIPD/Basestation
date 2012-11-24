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
        
def isNulls(data):
	for i in range(0,len(data)):
		if(data[i] != '\0'):
			return False
	return True
	
def getInput():
	global printNulls
	try:
		print "Waiting for input socket connection"
		listeningSocket = SocketConnection('',29877)
		print "Input connection created"
		if listeningSocket.connectAsReceiver():
			print "Connected as receiver"
			global isReady
			if not isReady:
				print "Waiting for ready message...."
				while True:
					data = listeningSocket.receiveData(1)
					if data == '*':
						print "Received ready message"
						isReady = True
						threading.Thread(target = starTimeouter).start()
						break
					else:
					    if printNulls:
					        print data.encode('hex_codec'),
			
			while True:
				data = listeningSocket.receiveData(32)
				if(not isNulls(data)):
					print "Writing: " + data.encode('hex_codec')
					serial.write(data)
		else:
			print "NO LISTENING CONNECTION"
	except:
		pass
	finally:
		listeningSocket.close()
		

def getKeys():
	global printNulls
	while True:
		k = raw_input()
		printNulls = not printNulls

def starTimeouter():
	global sendStars
	startTime = time.time()
	while sendStars:
		if(time.time() - startTime > 1):
			startTime = time.time()
			print "Sending Star"
			serial.write('*');


try:
	databuffer = []
	isReady = False
	printNulls = True
	sendStars = True
	
	serial = SerialConnection()
	print "Serial created"
	
	serial.connect("/dev/ttyUSB0")
	print "Serial Connected..."
	
	socketConnection = SocketConnection()
	
	print "Socket created"
	
	if(socketConnection.connectAsSender()):
		threading.Thread(target = sendLoop).start()
		threading.Thread(target = getInput).start()
		threading.Thread(target = getKeys).start()
		
		print 'Thread started'
		
		while not isReady:
			time.sleep(0.1)
		
		print "Sending speck ready message"
		serial.write('*')
		
		print "Removing nulls"
		serial.removeInitialNulls()
		sendStars = False
		
		print "NULLS REMOVED"
		
		databuffer.append('\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		
		while True:
			data = serial.read(32)
			print data.encode('hex_codec')
			databuffer.append(data)
		
		
		serial.close()
except:
	pass
finally:
	quit()
