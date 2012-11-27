#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SocketConnection import SocketConnection
from Packet import Packet
from random import randrange
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
                        break
            
            while True:
                data = listeningSocket.receiveData(32)
                if(not isNulls(data)):
                    print "Write: " + data.encode('hex_codec')
        else:
            print "NO LISTENING CONNECTION"
    except:
        pass
    finally:
        listeningSocket.close()

print sys.argv

try:
    databuffer = []
    isReady = False
    
    socketConnection = SocketConnection()
    
    print "Socket created"
    
    if(socketConnection.connectAsSender()):
        threading.Thread(target = sendLoop).start()
        threading.Thread(target = getInput).start()
       
        while not isReady:
            time.sleep(0.1)
        
        while True:
            time.sleep(1)
            data = '\x01\x00\x00\x01\x00\x00\x98\xdf\x4f'
            data += str(randrange(0,255) & 0xFF)
            data += '\xc7\x9e\xd0\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            
            print "READ: " + str(data.encode('hex_codec'))
            #data2 = '\x01\x00\x00\x01\x00\x00\x98\xdf\x4f\x03\xc7\x9e\xd0\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            databuffer.append(data)
except:
    raise
finally:
    quit()
