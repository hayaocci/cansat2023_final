'''
本番用のプログラム
'''
#-----モジュールのインポート-----#
import release
import land
import melt
#import parachute_avoid
import gps_running1
import human_detection
import photo_running
import stuck2
import send_photo

import bmx055
import bme280
import send
import motor
import traceback
import pigpio
import time
import gps
import take
#import paradetection
from machine_learning import DetectPeople
import sys
import calibration
import other
import datetime
import wgps_beta_photo_running as photo_running
import cv2
import save_photo as save_img
import beta_para_avoid as para_avoid
import wgps_beta_photo_running as imgguide
from math import sqrt
import test_PID as PID
from CONST import *
import module.log as log

###----------set up----------###

###-----clock setup-----###
t_start = time.time()

#-----log setup-----#
phase_log = log.Logger(dir='log/0_phase_log', filename='phase', t_start=t_start)
release_log = log.Logger(dir='log/1_release_log', filename='release', t_start=t_start)
land_log = log.Logger(dir='log/2_land_log', filename='land', t_start=t_start)
melt_log = log.Logger(dir='log/3_melt_log', filename='melt', t_start=t_start)
para_avoid_log = log.Logger(dir='log/4_para_avoid_log', filename='para_avoid', t_start=t_start)
gps_running_human_log = log.Logger(dir='log/5_gps_running_human_log', filename='gps_running_human', t_start=t_start)
human_detection_log = log.Logger(dir='log/6_human_detection_log', filename='human_detection', t_start=t_start)
gps_running_goal_log = log.Logger(dir='log/7_gps_running_goal_log', filename='gps_running_goal', t_start=t_start)
photo_running_log = log.Logger(dir='log/8_photo_running_log', filename='photo_running', t_start=t_start)

###-----sensor setup-----###
print("Starting Mission")

gps.open_gps()
bmx055.bmx055_setup()
bme280.bme280_setup()



###----------Mission Sequence----------###

###-----Release Detect Sequence-----###
print('Release Detect Sequence: Start')
release_log.save_log('start')


###-----Land Detect Sequence-----###
print('Land Detect Sequence: Start')

#-----Melt Sequence-----#
print('Melt Sequence: Start')


melt.main(meltPin=MELT_PIN, t_melt=MELT_TIME)
print('Melt Sequence: End')

#-----Parachute Avoid Sequence-----#
print('Parachute Avoid Sequence: Start')

stuck2.ue_jug()
time.sleep(15) #スタビライザーの復元待ち





print('Parachute Avoid Sequence: End')

#-----GPS Running Sequence to Human-----#

#-----Human Detection Sequence-----#

#-----GPS Running Sequence to Goal-----#

#-----Photo Running Sequence-----#
