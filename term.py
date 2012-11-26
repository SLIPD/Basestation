#!/usr/bin/env python

from SerialConnection import SerialConnection
import threading
import time
import sys
from payload import *
import socket


def sender():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    
    print "UDP target IP:", UDP_IP
    print "UDP target port:", UDP_PORT
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global dataBuffer
    while True:
        if(len(dataBuffer) > 0):
            sock.sendto(dataBuffer.pop(0), (UDP_IP, UDP_PORT))
        time.sleep(0.5)

def getMode():
    global printAll
    while True:
        p = raw_input()
        if(p == 'q'):
            global serial
            serial.close()
            sys.exit(0)
        printAll = not printAll
        
def logData(data):
    global dataBuffer
    dataBuffer.append(data)
    print data
    
dataBuffer = []
serial = SerialConnection()
serial.connect("/dev/tty.usbserial-FTG90JQK")
printAll = False
threading.Thread(target = getMode).start()
threading.Thread(target = sender).start()
while True:
    var = serial.readline()
    if printAll:
        logData(var)
    else:
        if var[:6] == "$GPGGA":
            parts = var.split(",")
            if(parts[2] != "" and parts[4] != ""):
                lat = float(parts[2])
                if parts[3] == "S":
                    lat = -lat
                long = float(parts[4])
                if parts[5] == "W":
                    long = -long
                p = PayloadNodePosition()
                (lat,long) = p.fixGooglesError((p.toDecimalDegrees(lat),p.toDecimalDegrees(long)))
                logData(str(lat) + "\t" + str(long))
        elif var[0] == ":":
            logData(var[:-1])
        elif (var[:6] == "$GPGSA" or var[:5] == "$PGSA"):
            parts = var.split(",")
            if(len(parts) < 16):
                logData(parts)
            else:
                logData(parts[15])
