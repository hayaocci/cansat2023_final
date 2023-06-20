import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/motor')
sys.path.append('/home/pi/git/kimuralab/Detection/GoalDetection')
import time
import traceback
import goal_detection
import motor

goalArea = 0		#variable for goal area
goalGAP = -1		#variable for goal gap
goalthd = 7000		#variable for goal area thd
H_min = 20			#Hue minimam
H_max = 20			#Hue maximam
S_thd = 80			#Saturation threshold


photopath = 		"/home/pi/photo/photo"

if __name__ == "__main__":
	try:
		f = 0
		while 1:
			if f == 0:
				#-----------------get information-----------------#
				motor.move(15, 15, 1.0)
				motor.move(0, 0, 1.0)
				goalFlug, goalArea, goalGAP, photoName = goal_detection.GoalDetection(photopath, H_min, H_max, S_thd, goalthd)
				print("flug", goalFlug, "area", goalArea, "GAP", goalGAP, "photoname", photoName)
				f = 1
			#-------------------motor debug-------------------#
			try:
				if f == 1:
					L = float(input("input left value "))
					f = 2
				if f == 2:
					R = float(input("input Right value "))
					f = 3
				if f == 3:
					T = float(input("input Time value "))
					motor.move(L, R, T)
					motor.move(0, 0, 2)
					motor.motor_stop()
					f = 0
			except KeyboardInterrupt:
				print("Emergency!")
				motor.motor_stop()
				sys.exit()
			except:
				pass
	except:
		motor.motor_stop()
		print(traceback.format_exc())