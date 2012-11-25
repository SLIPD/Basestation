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
                        #threading.Thread(target = starTimeouter).start()
                        break
            
            while True:
                data = listeningSocket.receiveData(32)
                if(not isNulls(data)):
                    print "Write: " + data.encode('hex_codec')
                    serial.write(data)
        else:
            print "NO LISTENING CONNECTION"
    except:
        pass
    finally:
        listeningSocket.close()


def starTimeouter():
    global sendStars
    global fakePacket
    startTime = time.time()
    while sendStars:
        if(time.time() - startTime > 1):
            startTime = time.time()
            if fakePacket:
                print "Sending Hash"
                serial.write('#')
            else:
                print "Sending Star"
                serial.write('*');


print sys.argv

try:
    fakePacket = False
    if len(sys.argv) == 2:
        fakePacket = True
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
        
        print 'Thread started'
        
        while not isReady:
            time.sleep(0.1)
        
        print "Sending speck ready message"
        
        if fakePacket:
            serial.write('#')
            serial.flush()
        else:
            serial.write('*')
            serial.flush()
        
        print "Removing nulls"
        #serial.removeInitialNulls()
        print serial.read(1)
        sendStars = False
        print "NULLS REMOVED"
        
        if fakePacket:
            print "Writing fake GPS packet"
            serial.write('\x00\x00\x00\x01\x00\x00\x03\x4F\xE7\x3F\x00\x01\xE9\x36\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        
        
        
        while True:
            data = serial.read(32)
            print "READ: " + str(data.encode('hex_codec'))
            databuffer.append(data)
        
        
        serial.close()
except:
    pass
finally:
    quit()
