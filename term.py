#!/usr/bin/env python

from SerialConnection import SerialConnection
import threading
import time
import sys

        


serial = SerialConnection()
serial.connect("/dev/tty.usbserial-FTG90JQK")
while True:
    val = serial.read(1)
    if val != None:
        print sys.stdout.write(val)
