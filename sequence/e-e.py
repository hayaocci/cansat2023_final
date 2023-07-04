import release
import land
import 3_melt#名前変更して
import 4_parachute_avoid#名前変更して
import gps_running1
import 6_human_detection#名前変更して
import gps_running2
import photo_running
import send
import bme280

if __name__=='__main__':
######--------------setup--------------######

######--------------release--------------######
    release()
    '''''
    thd_press_release = 0.1
    pressreleasecount = 0
    pressreleasejudge = 0
    t_delta_release = 10
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    press_d = 0

    while True:
        press_count_release, press_judge_release = pressdetect_release(thd_press_release, t_delta_release)
        print(f'count:{pressreleasecount}\tjudge{pressreleasejudge}')
        if press_count_release  >= 3:
            print('Press')
            send.send_data("TXDU 0001.0001")
            break
        else:
            print('unfulfilled')
    send.send_data("TXDU 0001.0002")

    '''''
######--------------land--------------######
    land()
    '''''
    print("Start")

    bme280.bme280_setup()
    bme280.bme280_calib_param()

    landcount = 0
    pressdata = [0.0, 0.0, 0.0, 0.0]

    while True:
        presslandjudge = 0
        landcount, presslandjudge = pressdetect_land(0.1)
        print(f'count:{landcount}\tjudge:{presslandjudge}')
        if presslandjudge == 1:
            print('Press')
            print('##--landed--##')
            break
        else:
            print('Press unfulfilled')
    '''''

######--------------melt--------------######
    3_melt()
    '''''
    try:
		down()
	except:
		pi.write(meltPin, 0)
    '''''

######--------------para_avoid--------------######
    4_parachute_avoid()
    '''''
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
            parachute_avoidance(flug, gap)
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
    '''''

######--------------run1--------------######
gps_running1()
'''''
    lat2 = 35.923914
    lon2 = 139.912223

    gps.open_gps()
    bmx055.bmx055_setup()
    motor.setup()

    drive(lon2, lat2, thd_distance=10, t_adj_gps=60)
'''''
######--------------mission--------------######
6_human_detection()
'''''
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
    lat_human = 35.923914
    lon_human = 139.912223

    ML_people = DetectPeople(model_path="model_mobile.tflite" )

    lat_n, lon_n, lat_e, lon_e, lat_s, lon_s, lat_w, lon_w = get_locations(lat_human, lon_human)

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
                break
        else:
            if elapsed_time >= threshold:  # 20分経ったか
                break_outer_loop = True
                break
            else:
                print("捜索続けます")
        motor.motor_move(1, -1, 0.5)  # 調整必要

    if human_judge_count==0:
        print ("青点エリア捜索に移行")
        for j in range(4):#4地点について行うよ
            elapsed_time = time.time()-start_time #経過時間の更新
            if break_outer_loop:
                break
            lat_now, lon_now = gps.location()
            move_to_bulearea()
            take_and_rotation()
'''''
######--------------run2--------------######
gps_running2()
#lon,latの値変えるだけでよさそう
######--------------goal--------------######
photo_running()
'''''
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
        lat2 = 35.923914
        lon2 = 139.912223

        G_thd = 60
        log_photorunning = '/home/dendenmushi/cansat2023/log/photorunning_practice.txt'
        motor.setup()

        # calibration
        #print_im920sl('##--calibration Start--##\n')
        magx_off, magy_off = calibration.cal(40, 40, 30)
        #print_im920sl(f'magx_off: {magx_off}\tmagy_off: {magy_off}\n')
        #print_im920sl('##--calibration end--##')

        # Image Guide
        image_guided_driving(log_photorunning, G_thd, magx_off,
                             magy_off, lon2, lat2, thd_distance=5, t_adj_gps=60)

    except KeyboardInterrupt:
        #print_im920sl('stop')
        print('stop')
        #im920sl2.off()
    except Exception as e:
        #im920sl2.off()
        tb = sys.exc_info()[2]
        #print_im920sl("message:{0}".format(e.with_traceback(tb)))

'''''