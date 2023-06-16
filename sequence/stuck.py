# -*- coding: utf-8 -*-
import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/BMX055')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/IM920')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Motor')
sys.path.append('/home/pi/git/kimuralab/IntegratedProgram/Running')
sys.path.append('/home/pi/git/kimuralab/Other')


import math
import pigpio
import time
import traceback

import bmx055
import Motor
import RunningGPS

stuck = 0
oLat = 0
oLon = 0
stuckNum = 0
stuckCount = 0
stuckStatus = 0

def stuckDetection(nLat = 0, nLon = 0):
	global oLat
	global oLon
	global stuckNum
	global stuckStatus
	distance = 0.0
	angle1, angle2 = 0.0, 0.0
	rollCount = 0

	for i in range(10):
		bmx055data = bmx055.bmx055_read()
		if(math.fabs(bmx055data[0]) >= 6):
			rollCount = rollCount + 1
		time.sleep(0.05)
	
	if(rollCount >= 8):
		#if rover has rolled over
		if(not stuckStatus == 1):
			stuckNum = 0
		stuckStatus = 1
		stuckNum = stuckNum + 1	
	elif(not nLon == 0.0):
		distance, angle1, angle2 = RunningGPS.calGoal(nLat, nLon, oLat, oLon, 0.0)
		if(distance <= 5):
			#if rover doesn't move
			if not stuckStatus == 2:
				stuckNum = 0
			stuckStatus = 2
			stuckNum = stuckNum + 1
		else:
			stuckStatus = 0
			stuckNum = 0
		oLat = nLat
		oLon = nLon
	print(stuckStatus, stuckNum, distance)
	return [stuckStatus, stuckNum]

def stuckEscape(mode = 0):
	# --- Mode --- #
	#   1 : Roll Over
	if(mode == 1):
		flug = 0
		count = 0
		while flug <= 5:
			# --- Restart --- #
			if(count == 0):
				Motor.motor(0, 0, 2)
				Motor.motor(40, 40, 2)
				Motor.motor(35, 35, 1)
				Motor.motor(28, 28, 1)
				count = 40
			Motor.motor(28, 28, 0.1)

			# --- Roll Over Check --- #
			if(stuckDetection() == 1):
				flug = flug + 1	#Not Roll Over
			else:
				flug = 0		#Roll Over
			count = count - 1 
		Motor.motor(0, 0, 2)
	else:
		pass   

if __name__ == "__main__":
	try:
		print(stuckDetection())
	except:
		Motor.motor(0, 0, 2)
		Motor.motor_stop()
		print(traceback.format_exc())
