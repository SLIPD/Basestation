#!/usr/bin/env python

from SocketConnection import SocketConnection
from Packet import Packet
from payload import *
import threading
import sys



def quit():
    print 'Quit() has been called'
    global listeningSocket
    global sendingSocket
    if(listeningSocket != None):
    	listeningSocket.close()
    if(sendingSocket != None):
    	sendingSocket.close()
    sys.exit()

def find_key(dic, val):
	keys = [k for k, v in dic.iteritems() if v == val]
	if(len(keys) > 0):
		return keys[0]
	return None

def assignId(speckid):
	global currentFreeAddress
	global ids
	payload = PayloadIdentification()
	address = find_key(ids,speckid)
	if address == None:
		ids[currentFreeAddress] = speckid
		payload.initialise(speckid,currentFreeAddress)
		currentFreeAddress += 1
	else:
		print "Bitching speck has already been identified"
		print ids
		payload.initialise(speckid,address)
	createAndSendPacket(0xFF,0x01,0x00,0x00,payload)

def createAndSendPacket(destinationId,ttl,msgType,timestamp,payload):
	p = Packet()
	p.initialise(0,destinationId,ttl,msgType,timestamp,payload)
	print "Creating and Sending: "
	print p
	global sendingSocket
	sendingSocket.sendData(p.getBytes())

def sendStartInstruction():
	sendingSocket.sendData('*')

def getKeyInput():
		print "\n\nPress enter to start... ",
		data = raw_input()
		sendStartInstruction()
		print "Send initialising data"


ids = {}
currentFreeAddress = 1

listeningSocket = None
sendingSocket = None

try:
	listeningSocket = SocketConnection('localhost')
		
	if(listeningSocket.connectAsReceiver()):
		sendingSocket = SocketConnection('', 29877)
		if(not sendingSocket.connectAsSender()):
			print "Could not connect as sender"
		else :
			threading.Thread(target = getKeyInput).start()
			while(True):
				
				data = listeningSocket.receiveData()
				packet = Packet(data)
				print "Current Packet: "
				print packet
				if(packet.isIdentification()):
					print "Identification packet!"
					assignId(packet.getPayload().getId())
				else:
					print "Not Identification"
	else:
		print "Could not connect as receiver"
		
except Exception, e:
	print "Exception: %s" % e
finally:
	print "Finally: "
	quit()

