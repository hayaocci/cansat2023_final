# -*- coding: utf-8 -*-

import serial
import binascii
import signal
import sys
import platform
import pigpio
import time
portnumber = '/dev/ttyAMA0'

def testsend():
	com.flushInput()
	setspeed = input("何する？")
	com.write( setspeed.encode('utf-8') )
	com.flushOutput()
	text = com.readline().strip()
	print("受信 : " + text )


if __name__ == '__main__':
	
    while True:
	    testsend()
