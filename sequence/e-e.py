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

#variable for log
log_phase=other.filename('/home/dendenmushi/cansat2023/sequence/log/phaselog','txt')
log_release=other.filename('/home/dendenmushi/cansat2023/sequence/log/releaselog','txt')
log_landing=other.filename('/home/dendenmushi/cansat2023/sequence/log/landinglog','txt')
log_melting=other.filename('/home/dendenmushi/cansat2023/sequence/log/meltinglog','txt')
log_para=other.filename('/home/dendenmushi/cansat2023/sequence/log/para_avoid_log','txt')
log_gpsrunning1=other.filename('/home/dendenmushi/cansat2023/sequence/log/gpsrunning1log','txt')
log_humandetect=other.filename('/home/dendenmushi/cansat2023/sequence/log/humandetectlog','txt')
log_gpsrunning2=other.filename('/home/dendenmushi/cansat2023/sequence/log/gpsrunning2log','txt')
log_photorunning =other.filename( '/home/dendenmushi/cansat2023/sequence/log/photorunninglog','txt')

if __name__=='__main__':

###----------set up -----------###
    t_start=time.time()
    print("START: Setup")
    other.log(log_phase,'1',"setup phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    bme280.bme280_setup()
    bme280.bme280_calib_param()

    #release
    thd_press_release = 0.1
    timeout_release = time.time()+(0.5*60)
    #land
    landcount = 0
    pressdata = [0.0, 0.0, 0.0, 0.0]
    # timeout_land = time.time() + (0.5*60)
    #para
    # motor.setup()
    #run1
    gps.open_gps()
    bmx055.bmx055_setup()

    #人の座標
    #グランドの中央
    # lat_human = 35.9243068
    # lon_human = 139.9124594
    #中庭
    lat_human =35.918329 
    lon_human =139.907841
    #ゴール座標
    #グランドのゴール前
    # lat_goal = 35.923914
    # lon_goal = 139.912223
    #中庭
    lat_goal = 35.918329
    lon_goal = 139.907841
 
###-------release judge -------###
    print("START: Release judge")
    other.log(log_phase,'2',"release phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    thd_press_release = 0.1
    # pressreleasecount = 0
    # pressreleasejudge = 0
    t_delta_release = 10
    #タイムアウトを20分に設定
    #timeout_release = time.time()+(0.5*60)
    # bme280.bme280_setup()
    # bme280.bme280_calib_param()
    # press_d = 0

    other.log(log_release, "release judge start")
    #while True:
    while time.time() < timeout_release:
        press_count_release, press_judge_release = release.pressdetect_release(thd_press_release, t_delta_release)
        print(f'count:{press_count_release}\tjudge:{press_judge_release}')
        other.log(log_release, datetime.datetime.now(), time.time() - t_start,
                          bme280.bme280_read(), press_count_release, press_judge_release)
        if press_count_release  > 3:
            print('Release')
            send.send_data("TXDU 0001.A001")
            break
        else:
            print('unfulfilled')
    other.log(log_release, "release judge finish")
    send.send_data("TXDU 0001.AAAA")
    print("release finish!!!")
    ###-------land judge -------###
    print("START: Land judge")
    other.log(log_phase,'3',"land phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    send.send_data("TXDU 0001,B000")

    #bme280.bme280_setup()
    #bme280.bme280_calib_param()

    # landcount = 0
    # pressdata = [0.0, 0.0, 0.0, 0.0]
    #タイムアウトを20分に設定
    timeout_land = time.time() + (0.5*60)

    other.log(log_landing, "land judge start")
    #while True:
    while time.time() < timeout_land:
        presslandjudge = 0
        landcount, presslandjudge, delta_p, Prevpress, latestpress = land.pressdetect_land(0.1)
        print(f'count:{landcount}\tjudge:{presslandjudge}')
        other.log(log_landing, datetime.datetime.now(), time.time() - t_start,
                           bme280.bme280_read(),landcount,presslandjudge)
        if presslandjudge == 1:
            print('Press')
            send.send_data("TXDU 0001,B002")
            print('##--landed--##')
            break
        else:
            print('Press unfulfilled')
            send.send_data("TXDU 0001,B001")
    other.log(log_landing, "land judge finish")
    send.send_data("TXDU 0001,BBBB")
    print("land finish!!!")
    ###-------melt-------###

    print("START: Melt")
    other.log(log_phase,'4',"melt phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    pi = pigpio.pi()

    meltPin = 4
    other.log(log_melting, datetime.datetime.now(), time.time() - t_start,  "melt start")
    try:
        melt.down()
        send.send_data("TXDU 0001,C001")
    except:
        pi.write(meltPin, 0)

    other.log(log_melting, datetime.datetime.now(), time.time() - t_start,  "melt finish")
    send.send_data("TXDU 0001,CCCC")
    print("melt finish!!!")
    ###------paraavo-------###
    # try:
    #     motor.setup()

    #     print("START: Parachute avoidance")
    #     other.log(log_phase,'5',"Paraavo phase",datetime.datetime.now(),time.time()-t_start)
    #     phase=other.phase(log_phase)
    #     other.log(log_paraavoidance,"paraavo start")

    #     flug, area, gap, photoname = paradetection.para_detection("photostorage/photostorage_paradete/para", 320, 240,
    #                                                               200, 10, 120, 1)
    #     print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
    #     other.log(log_paraavoidance, datetime.datetime.now(), time.time() -
    #                   t_start, flug, area, gap, photoname)
    #     print("paradetection phase success")
    #     count_paraavo = 0
    #     while count_paraavo < 3:
    #         flug, area, gap, photoname = paradetection.para_detection("photostorage/photostorage_paradete/para", 320,
    #                                                                   240, 200, 10, 120, 1)
    #         print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
    #         other.log(log_paraavoidance, datetime.datetime.now(), time.time() -
    #                   t_start, flug, area, gap, photoname,count_paraavo)
    #         parachute_avoid.parachute_avoidance(flug, gap)
    #         print(flug)
    #         if flug == -1 or flug == 0:
    #             count_paraavo += 1
    #             print(count_paraavo)

    #     print("パラシュート回避完了")

    # except KeyboardInterrupt:
    #     print("emergency!")

    # except:
    #     print(traceback.format_exc())
    # print("finish!")
    # other.log(log_phase,'5',"Paraavo phase",datetime.datetime.now(),time.time()-t_start)
    # phase=other.phase(log_phase)
    # other.log(log_paraavoidance,"paraavo start")
    # #motor.setup()
    # red_area, angle = para_avoid.detect_para()
    # para_avoid.para_avoid(red_area, angle, check_count=5)
    # other.log(log_paraavoidance,"paraavo finish")
    #-----上ジャッジ-----#
    # motor.setup()
    stuck2.ue_jug()

    #-----スタビの復元まち-----#
    time.sleep(15)

    #-----praschute avoid-----#
    other.log(log_para, datetime.datetime.now(), "Parachute avoidance Start")
    red_area, angle = para_avoid.detect_para()
    para_avoid.para_avoid(red_area, angle, check_count=5)
    other.log(log_para, datetime.datetime.now(), "Parachute avoidance Finish")
    send.send_data("TXDU 0001,DDDD")

    print("paraavo finish!!!")
######--------------run1--------------######
    print("START:gps running1")
    other.log(log_phase,'6',"gps running1 phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)

    # gps.open_gps()
    # bmx055.bmx055_setup()
    # motor.setup()
    other.log(log_gpsrunning1,"run1 start")
    goal_distance = gps_running1.drive(lon_human, lat_human, thd_distance=5, t_adj_gps=60,logpath=log_gpsrunning1)
    print(f'-----distance: {goal_distance}-----')
    other.log(log_gpsrunning1,"run1 finish")
    print("finish!")
######--------------mission--------------######
    print("START:human detect")
    other.log(log_phase,'7',"humandetect phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    count = 0
    human_judge_count=0
    break_outer_loop =False
    start_time = time.time()
    threshold = 20 * 60
    elapsed_time = time.time()-start_time

    ML_people = DetectPeople(model_path="model_mobile.tflite" )

    lat_n, lon_n, lat_e, lon_e, lat_s, lon_s, lat_w, lon_w = human_detection.get_locations(lat_human, lon_human)
    
    other.log(log_humandetect,"humandetect start")
    #まずはメインエリアを捜索
    for k in range(24):
        if break_outer_loop == False:
            human_judge_count = 0
            #撮影
            img_path = take.picture('ML_imgs/image', 320, 240)
            
            #モデルの読み込み
            result = ML_people.predict(image_path=img_path)
            other.log(log_humandetect, datetime.datetime.now(), time.time() -
                      t_start,result,0,human_judge_count,break_outer_loop,elapsed_time)

            #hitoの確率80%かどうか
            if result >= 0.80:
                human_judge_count += 1
                # 追加の写真を撮影
                for h in range(2):
                    additional_img_path = take.picture('ML_imgs/additional_image', 320, 240)
                    additional_result = ML_people.predict(image_path=additional_img_path)
                    other.log(log_humandetect, datetime.datetime.now(), time.time() -
                      t_start,result,additional_result,human_judge_count,break_outer_loop,elapsed_time)

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
                human_judge_count, break_outer_loop = human_detection.take_and_rotation(human_judge_count=human_judge_count, break_outer_loop=break_outer_loop,logpath=log_humandetect)
    if human_judge_count==3:
        t_start = time.time()

        chunk_size = 4   # 送る文字数。この数字の2倍の文字数が送られる。1ピクセルの情報は16進数で6文字で表せられるため、6の倍数の文字を送りたい。
        delay = 3   # 伝送間隔（秒）
        num_samples = 10 #GPSを読み取る回数
        photo_quality = 30 #伝送する画像の圧縮率
        count = 0
        count_v = 0
        count_error = 0
        id_counter = 1

        while True:
            try:
                utc, lat, lon, sHeight, gHeight = gps.read_gps()
                if utc == -1.0:
                    if lat == -1.0:
                        print("Reading gps Error")
                        count_error = count_error +1
                        if count_error > num_samples:
                            send.send_data("human_GPS_start")
                            print("human_GPS_start")
                            time.sleep(delay)
                            send.send_data("Reading gps Error")
                            print("Reading gps Error")
                            time.sleep(delay)
                            send.send_data("human_GPS_fin")
                            print("human_GPS_fin")
                            time.sleep(delay)
                            break
                        # pass
                    else:
                        # pass
                        print("Status V")
                        count_v = count_v + 1
                        if count_v > num_samples:
                            time.sleep(delay)
                            send.send_data("human_GPS_start")
                            print("human_GPS_start")
                            time.sleep(delay)
                            send.send_data("Status V")
                            print("Status V")
                            time.sleep(delay)
                            send.send_data("human_GPS_fin")
                            print("human_GPS_fin")
                            time.sleep(delay)
                            break
                else:
                    # pass
                    print(utc, lat, lon, sHeight, gHeight)
                    lat, lon = gps.location()
                    print(lat,lon)
                    count = count +1
                    if count % num_samples == 0:
                        send_lat = lat
                        send_lon = lon
                        print(send_lat,send_lon)
                    # 無線で送信
                        time.sleep(delay)
                        send.send_data("human_GPS_start")
                        print("human_GPS_start")
                        time.sleep(delay)
                        send.sed_data(send_lat,send_lon)
                        print(send_lat,send_lon)
                        time.sleep(delay)
                        send.send_data("human_GPS_fin")
                        print("human_GPS_fin")
                        time.sleep (delay)
                        break
                time.sleep(1)
            except KeyboardInterrupt:
                send_photo.close_gps()
                print("\r\nKeyboard Intruppted, Serial Closed")
            except:
                send_photo.close_gps()
                print(traceback.format_exc())
        


        
        
    #---------------------画像伝送----------------------------#
    
        time.sleep(15)
        file_name = "/home/dendenmushi/cansat2023/sequence/ML_imgs/jpg"  # 保存するファイル名を指定
        photo_take = take.picture(file_name, 320, 240)
        print("撮影した写真のファイルパス：", photo_take)
        
        # 入力ファイルパスと出力ファイルパスを指定してリサイズ
        input_file = photo_take    # 入力ファイルのパスを適切に指定してください
        photo_name = "/home/dendenmushi/cansat2023/sequence/ML_imgs/send_photo_resize.jpg"  # 出力ファイルのパスを適切に指定してください
        new_width = 60            # リサイズ後の幅を指定します
        new_height = 80           # リサイズ後の高さを指定します

        # リサイズを実行
        send_photo.resize_image(input_file, photo_name, new_width, new_height)
        
        print("写真撮影完了")
        
        # 圧縮したい画像のパスと出力先のパスを指定します
        input_image_path = photo_name
        compressed_image_path = 'compressed_test.jpg'
        
        # 圧縮率を指定します（0から100の範囲の整数）
        compression_quality = photo_quality
        
        # 画像を圧縮します
        send_photo.compress_image(input_image_path, compressed_image_path, compression_quality)
        
        # 圧縮後の画像をバイナリ形式に変換します
        with open(compressed_image_path, 'rb') as f:
            compressed_image_binary = f.read()
        
        
        data = compressed_image_binary  # バイナリデータを指定してください
        output_filename = "output.txt"  # 保存先のファイル名
        
        start_time = time.time()  # プログラム開始時刻を記録
        
        send.send_data ("wireless_start")

        print("写真伝送開始します")
        time.sleep(1)

        
        # バイナリデータを32バイトずつ表示し、ファイルに保存する
        with open(output_filename, "w") as f:
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i+chunk_size]
                chunk_str = "".join(format(byte, "02X") for byte in chunk)
                
                # 識別番号とデータを含む行の文字列を作成
                line_with_id = f"{id_counter}-{chunk_str}"

                #chunk_strにデータがある
                print(line_with_id)
                send.send_data(line_with_id)
                # 表示間隔を待つ
                time.sleep(delay)
                id_counter = id_counter +1
        
                # ファイルに書き込む
                f.write(line_with_id + "\n")

        send.send_data ("wireless_fin")
        send.send_data("num=" + str(id_counter))
        
        end_time = time.time()  # プログラム終了時刻を記録
        execution_time = end_time - start_time  # 実行時間を計算
        
        print("実行時間:", execution_time, "秒")
        print("データを", output_filename, "に保存しました。")            
    other.log(log_humandetect,"humandetect finish")
    print("human detection finish!!!")
######--------------run2--------------######
    other.log(log_phase,'8',"gps running2 phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    other.log(log_gpsrunning2,"run2 start")
    gps_running1.drive(lon_goal, lat_goal, thd_distance=5, t_adj_gps=50,logpath=log_gpsrunning2)
    print(f'-----distance: {goal_distance}-----')
    other.log(log_gpsrunning2,"run2 finish")
    print("finish!")

######--------------goal--------------######
    other.log(log_phase,'9',"goal phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    other.log(log_photorunning,"photorun start")
    try:
        angle = 0
        t_running = 0

        area_ratio, angle = imgguide.detect_goal(lat_goal, lon_goal)
        imgguide.image_guided_driving(area_ratio, angle, lat_goal, lon_goal)
    except:
        other.log(log_photorunning,"photorun finish")
        print("photorun finish")
        other.log(log_phase,'10',"all phase complete",datetime.datetime.now(),time.time()-t_start)
        print("all complete!")
