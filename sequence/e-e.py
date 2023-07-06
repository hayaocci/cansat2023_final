import release
import land
import melt
import parachute_avoid
import gps_running1
import human_detection
import photo_running

import bmx055
import bme280
import send
import motor
import traceback
import pigpio
import time
import gps
import take
import paradetection
from machine_learning import DetectPeople
import sys
import calibration


if __name__=='__main__':
###-------release judge -------###
    print("START: Release judge")
    thd_press_release = 0.1
    pressreleasecount = 0
    pressreleasejudge = 0
    t_delta_release = 10
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    press_d = 0

    while True:
        press_count_release, press_judge_release = release.pressdetect_release(thd_press_release, t_delta_release)
        print(f'count:{pressreleasecount}\tjudge{pressreleasejudge}')
        if press_count_release  > 3:
            print('Press')
            send.send_data("TXDU 0001.A001")
            break
        else:
            print('unfulfilled')

    send.send_data("TXDU 0001.AAAA")

    ###-------land judge -------###
    print("START: Land judge")
    send.send_data("TXDU 0001,B000")

    #bme280.bme280_setup()
    #bme280.bme280_calib_param()

    landcount = 0
    pressdata = [0.0, 0.0, 0.0, 0.0]

    while True:
        presslandjudge = 0
        landcount, presslandjudge = land.pressdetect_land(0.1)
        print(f'count:{landcount}\tjudge:{presslandjudge}')
        if presslandjudge == 1:
            print('Press')
            send.send_data("TXDU 0001,B002")
            print('##--landed--##')
            break
        else:
            print('Press unfulfilled')
            send.send_data("TXDU 0001,B001")

    send.send_data("TXDU 0001,BBBB")
    ###-------melt-------###

    print("START: Melt")
    pi = pigpio.pi()

    meltPin = 4
    try:
        melt.down()
        send.send_data("TXDU 0001,C001")
    except:
        pi.write(meltPin, 0)
    
    send.send_data("TXDU 0001,CCCC")
    ###------paraavo-------###
    try:
        motor.setup()

        print("START: Parachute avoidance")

        flug, area, gap, photoname = paradetection.para_detection("photostorage/photostorage_paradete/para", 320, 240,
                                                                  200, 10, 120, 1)
        print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
        print("paradetection phase success")
        count_paraavo = 0
        while count_paraavo < 3:
            flug, area, gap, photoname = paradetection.para_detection("photostorage/photostorage_paradete/para", 320,
                                                                      240, 200, 10, 120, 1)
            print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
            parachute_avoid.parachute_avoidance(flug, gap)
            print(flug)
            if flug == -1 or flug == 0:
                count_paraavo += 1
                print(count_paraavo)

        print("パラシュート回避完了")

    except KeyboardInterrupt:
        print("emergency!")

    except:
        print(traceback.format_exc())
    print("finish!")

    send.send_data("TXDU 0001,DDDD")


######--------------run1--------------######
    #生協入口
    #lat2 = 35.91818718
    #lon2 = 139.90814829

    #12号館前
    #lat2 = 35.91896917
    #lon2 = 139.90859362

    #グランドのゴール前
    #lat2 = 35.923914
    #lon2 = 139.912223

    #狭いグランドのほう
    #lat2 = 35.9243874
    #lon2 = 139.9114187

    #中庭の芝生
    lat2 = 35.91817415
    lon2 = 139.90825559

    #実験棟の前
    #lat2 = 35.9189778
    #lon2 = 139.9071493 
    gps.open_gps()
    bmx055.bmx055_setup()
    motor.setup()

    gps_running1.drive(lon2, lat2, thd_distance=10, t_adj_gps=100)
######--------------mission--------------######
    count = 0
    human_judge_count=0
    break_outer_loop =False
    start_time = time.time()
    threshold = 20 * 60
    elapsed_time = time.time()-start_time
    #lat1 = 35.12345 #赤点
    #lon1 = 139.67890 #赤点

    #12号館前
    #lat_human = 35.91896917
    #lon_human = 139.90859362

    #グランドのゴール前
    #lat_human = 35.923914
    #lon_human = 139.912223

    #lat_human = 35.9243467
    #lon_human = 139.9113996

    #中庭の芝生
    lat_human = 35.91817415
    lon_human = 139.90825559

    ML_people = DetectPeople(model_path="model_mobile.tflite" )

    lat_n, lon_n, lat_e, lon_e, lat_s, lon_s, lat_w, lon_w = human_detection.get_locations(lat_human, lon_human)

    #まずはメインエリアを捜索
    for k in range(6):

        #撮影
        img_path = take.picture('ML_imgs/image', 320, 240)
        
        #モデルの読み込み
        result = ML_people.predict(image_path=img_path)

        # result=machine_learning.pro_people()
        #hitoの確率50%かどうか
        if result >= 0.50:
            human_judge_count += 1
            # 追加の写真を撮影
            for h in range(2):
                additional_img_path = take.picture('ML_imgs/additional_image', 320, 240)
                additional_result = ML_people.predict(image_path=additional_img_path)
                if additional_result >= 0.50:
                    human_judge_count += 1
                    if human_judge_count >= 3:
                        break_outer_loop = True
                        print("遭難者発見")
                        break
            if break_outer_loop:
                human_judge_count = 0
                break
        else:
            if elapsed_time >= threshold:  # 20分経ったか
                break_outer_loop = True
                break
            else:
                print("捜索続けます")
        motor.move(50, -50, 0.5)  # 調整必要

    if human_judge_count==0:
        print ("青点エリア捜索に移行")
        for j in range(4):#4地点について行うよ
            elapsed_time = time.time()-start_time #経過時間の更新
            if break_outer_loop:
                break
            lat_now, lon_now = gps.location()
            human_detection.move_to_bulearea(count)
            human_detection.take_and_rotation(break_outer_loop, human_judge_count)
######--------------run2--------------######
    gps_running1.drive(lon2, lat2, thd_distance=10, t_adj_gps=100)
#lon,latの値変えるだけでよさそう
######--------------goal--------------######
    try:
        # Initialize
        #lat2 = 35.9192621
        #lon2 = 139.9085065
        #lat2 = 35.91818718
        #lon2 = 139.90814829

        #12号館前
        #lat2 = 35.91896917
        #lon2 = 139.90859362

        #グランドのゴール前
        #lat2 = 35.923914
        #lon2 = 139.912223

        #lat2 = 35.9243426
        #lon2 = 139.9112739

        #中庭の芝生
        lat2 = 35.91817415
        lon2 = 139.90825559

        G_thd = 60
        log_photorunning = '/home/dendenmushi/cansat2023/log/photorunning_practice.txt'
        motor.setup()

        # calibration
        #print_im920sl('##--calibration Start--##\n')
        magx_off, magy_off = calibration.cal(40, 40, 30)
        #print_im920sl(f'magx_off: {magx_off}\tmagy_off: {magy_off}\n')
        #print_im920sl('##--calibration end--##')

        # Image Guide
        photo_running.image_guided_driving(log_photorunning, G_thd, magx_off,
                             magy_off, lon2, lat2, thd_distance=5, t_adj_gps=10)

    except KeyboardInterrupt:
        #print_im920sl('stop')
        print('stop')
        #im920sl2.off()
    except Exception as e:
        #im920sl2.off()
        tb = sys.exc_info()[2]