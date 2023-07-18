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
import other

#variable for log
log_release=other.filename('/home/dendenmushi/cansat2023/sequence/log/releaselog','txt')
log_landing=other.filename('/home/dendenmushi/cansat2023/sequence/log/landinglog','txt')
log_melting=other.filename('/home/dendenmushi/cansat2023/sequence/log/meltinglog','txt')
log_paraavoidance=other.filename('/home/dendenmushi/cansat2023/sequence/log/paraavoidancelog','txt')
log_gpsrunning1=other.filename('/home/dendenmushi/cansat2023/sequence/log/gpsrunning1log','txt')
log_humandetect=other.filename('/home/dendenmushi/cansat2023/sequence/log/humandetectlog','txt')
log_gpsrunning2=other.filename('/home/dendenmushi/cansat2023/sequence/log/gpsrunning2log','txt')


if __name__=='__main__':

###----------set up -----------###
    #グランドの中央
    lat_human = 35.9243068
    lon_human = 139.9124594

    #グランドのゴール前
    lat_goal = 35.923914
    lon_goal = 139.912223
 
###-------release judge -------###
    print("START: Release judge")
    thd_press_release = 0.1
    # pressreleasecount = 0
    # pressreleasejudge = 0
    t_delta_release = 10
    #タイムアウトを20分に設定
    timeout_release = time.time()+(20*60)
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    # press_d = 0

    #while True:
    while time.time() < timeout_release:
        press_count_release, press_judge_release = release.pressdetect_release(thd_press_release, t_delta_release)
        print(f'count:{press_count_release}\tjudge:{press_judge_release}')
        if press_count_release  > 3:
            print('Release')
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
    #タイムアウトを20分に設定
    timeout_land = time.time() + (20*60)
    #while True:
    while time.time() < timeout_land:
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
    print("START:gps running1")

    gps.open_gps()
    bmx055.bmx055_setup()
    motor.setup()

    goal_distance = gps_running1.drive(lon_human, lat_human, thd_distance=10, t_adj_gps=100)
    print(f'-----distance: {goal_distance}-----')
    print("finish!")
######--------------mission--------------######
    count = 0
    human_judge_count=0
    break_outer_loop =False
    start_time = time.time()
    threshold = 20 * 60
    elapsed_time = time.time()-start_time

    ML_people = DetectPeople(model_path="model_mobile.tflite" )

    lat_n, lon_n, lat_e, lon_e, lat_s, lon_s, lat_w, lon_w = human_detection.get_locations(lat_human, lon_human)

    #まずはメインエリアを捜索
    for k in range(24):
        if break_outer_loop == False:
            human_judge_count = 0
            #撮影
            img_path = take.picture('ML_imgs/image', 320, 240)
            
            #モデルの読み込み
            result = ML_people.predict(image_path=img_path)

            #hitoの確率80%かどうか
            if result >= 0.80:
                human_judge_count += 1
                # 追加の写真を撮影
                for h in range(2):
                    additional_img_path = take.picture('ML_imgs/additional_image', 320, 240)
                    additional_result = ML_people.predict(image_path=additional_img_path)
                    if additional_result >= 0.80:
                        human_judge_count += 1
                        if human_judge_count >= 3:
                            break_outer_loop = True
                            print("遭難者発見")
                            break
                    else:
                        human_judge_count = 0
            else:
                if elapsed_time >= threshold:  # 20分経ったか
                    break_outer_loop = True
                    break
                else:
                    print("捜索続けます")
            #motor.move(35, -35, 0.2) # 芝生の上
            motor.move(20, -20, 0.2) #グランド
        else:
            break
    if break_outer_loop == False:
        print("24回撮影しました")
        print("次のエリアに移動します")


    if human_judge_count==0:
        print ("青点エリア捜索に移行")
        for j in range(4):#4地点について行うよ
            elapsed_time = time.time()-start_time #経過時間の更新
            if break_outer_loop == True:
                break
            else:
                lat_now, lon_now = gps.location()
                count += 1
                human_detection.move_to_bulearea(count, lat_human, lon_human)
                human_judge_count, break_outer_loop = human_detection.take_and_rotation(human_judge_count=human_judge_count, break_outer_loop=break_outer_loop)
                if j ==4 and break_outer_loop == False:
                    print("おらんやないか、もう帰るわ")

    print("human detection finish!!!")
######--------------run2--------------######
    gps_running1.drive(lon_goal, lat_goal, thd_distance=10, t_adj_gps=100)
    print(f'-----distance: {goal_distance}-----')
    print("finish!")
######--------------goal--------------######
    try:
        G_thd = 40
        log_photorunning = '/home/dendenmushi/cansat2023/log/photorunning_practice.txt'
        motor.setup()

        # calibration
        #print_im920sl('##--calibration Start--##\n')
        magx_off, magy_off = calibration.cal(40,-40, 30)
        #print_im920sl(f'magx_off: {magx_off}\tmagy_off: {magy_off}\n')
        #print_im920sl('##--calibration end--##')

        # Image Guide
        photo_running.image_guided_driving(log_photorunning, G_thd, magx_off,
                             magy_off, lon_goal, lat_goal, thd_distance=5, t_adj_gps=10)

    except KeyboardInterrupt:
        #print_im920sl('stop')
        print('stop')
        #im920sl2.off()
    except Exception as e:
        #im920sl2.off()
        tb = sys.exc_info()[2]
        #print_im920sl("message:{0}".format(e.with_traceback(tb)))