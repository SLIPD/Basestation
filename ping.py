#!/usr/bin/env python

from SerialConnection import SerialConnection
from Packet import Packet
from payload import *
import threading
import time
import sys
import struct
from Timer import *

def quit():
    print 'Exiting...'
    sys.exit()


try:
    databuffer = []

    serial = SerialConnection()
    print "Serial created"

    serial.connect("/dev/tty.usbserial-FTG90JQK")
    print "Serial Connected..."

    print "Removing nulls"
    serial.removeInitialNulls()
    print "NULLS REMOVED"
    counter = -1
    while True:
        #a = raw_input()
        counter += 1
        if counter > 255:
            counter = 0
        #senddata = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00'
        senddata = struct.pack('QQQBBBBBBBB',0,0,0,counter,0,0,0,0,0,0,0)
        with Timer() as t:
            #print "pinging with " + str(len(senddata)) + " bytes of data"
            serial.write(senddata)
            data = serial.read(32)
        if(data != ''):
            print str(t.interval)
            #print "DATA: " + str(data.encode('hex_codec'))
        else:
            print "TIMEOUT"

    serial.close()
except:
    pass
finally:
    quit()
