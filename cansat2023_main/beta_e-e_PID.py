import release
import land
import melt
#import parachute_avoid
import beta_gps_running as gps_running
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
import cv2
import save_photo as save_img
import beta_para_avoid as para_avoid
import wgps_beta_photo_running as imgguide
from math import sqrt
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

def get_locations(lat_human, lon_human):
#最後の位置情報をもとに周囲の4つの点の座標を求める

    #北緯40度における10mあたりの緯度経度の差
    #緯度は0.3236246秒　経度は0.3242秒
    #lat_dif = 0.0000323
    #lon_dif = 0.0000324

    lat_dif = 0.0000090
    lon_dif = 0.0000110

    #北緯40度における10mあたりの緯度経度の差
    #lon_dif = 0.0000117
    
    #捜索範囲の四角形の一辺の長さ
    side_length = 40

    #赤点から青点までの距離 red to blue distance
    rtb_distance = (side_length/4)*sqrt(2) 

    #周囲の4つの位置を求める
    #north
    lat_n = lat_human + lat_dif*(rtb_distance)
    lon_n = lon_human
    #east
    lat_e = lat_human
    lon_e = lon_human - lon_dif*(rtb_distance)
    #south
    lat_s = lat_human - lat_dif*(rtb_distance)
    lon_s = lon_human
    #west
    lat_w = lat_human
    lon_w = lon_human + lon_dif*(rtb_distance)

    return {
        'lat_n':lat_n,
        'lon_n':lon_n,
        'lat_e':lat_e,
        'lon_e':lon_e,
        'lat_s':lat_s,
        'lon_s':lon_s,
        'lat_w':lat_w,
        'lon_w':lon_w
        }

def take_and_rotation(human_judge_count, break_outer_loop,logpath, model):


    #for i in range(6):
    for i in range(24):
        if break_outer_loop == False:
            human_judge_count = 0
            # 撮影
            img_path = take.picture('ML_imgs/image', 320, 240)

            # モデルの読み込み
            #result = ML_people.predict(image_path=img_path)
            result = model.predict(image_path=img_path)
            other.log(logpath, datetime.datetime.now(), time.time() -
                      t_start,result,additional_result,human_judge_count,break_outer_loop,elapsed_time)
            # hitoの確率80%かどうか
            if result >= 0.80:
                human_judge_count += 1
                print(human_judge_count)
                # 追加の写真を撮影
                for j in range(2):
                    additional_img_path = take.picture('ML_imgs/additional_image', 320, 240)
                    #additional_result = ML_people.predict(image_path=additional_img_path)
                    additional_result = model.predict(image_path=additional_img_path)
                    other.log(logpath, datetime.datetime.now(), time.time() -
                      t_start,result,additional_result,human_judge_count,break_outer_loop,elapsed_time)
                    if additional_result >= 0.80:
                        human_judge_count += 1
                        print(human_judge_count)
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
            #motor.move(30, -30, 0.2)  # 芝生の上
            motor.move(20, -20, 0.25)  #グランド
        else:
            break
    if break_outer_loop == False:
        print("24回撮影しました")
        print("次のエリアに移動します")
    return human_judge_count , break_outer_loop

    
def move_to_bulearea(count, lat_human, lon_human):
 
    # data_dist_bulearea1 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat_n,lon_n)
    # data_dist_bulearea2 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat_e,lon_e)
    # data_dist_bulearea3 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat_s,lon_s)
    # data_dist_bulearea4 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat_w,lon_w)

    
    blue_loc = get_locations(lat_human, lon_human)
    lat_n = blue_loc['lat_n']
    lon_n = blue_loc['lon_n']
    lat_e = blue_loc['lat_e']
    lon_e = blue_loc['lon_e']
    lat_s = blue_loc['lat_s']
    lon_s = blue_loc['lon_s']
    lat_w = blue_loc['lat_w']
    lon_w = blue_loc['lon_w']


    print(count)
    #青点から5m以内か
    if count == 1:
        # condition =1
        # while condition == 1:
        #     if data_dist_bulearea1['distance']<=5:
        #         print("第"+count+"エリア到着")
        #         condition =0
        #     print("第"+count+"エリア外です")
        gps_running.drive(lon_n, lat_n, thd_distance=3, t_adj_gps=60)#60秒もいるのか？
        print("第1エリアです")
    elif count == 2:
        # condition =1
        # while condition == 1:
        #     if data_dist_bulearea2['distance']<=5:
        #         print("第"+count+"エリア到着")
        #         condition =0
        #     print("第"+count+"エリア外です")
        gps_running.drive(lon_e, lat_e, thd_distance=3, t_adj_gps=60) 
        print("第2エリアです")  
    elif count == 3:
        # condition =1
        # while condition == 1:
        #     if data_dist_bulearea3['distance']<=5:
        #         print("第"+count+"エリア到着")
        #         condition =0
        #     print("第"+count+"エリア外です")
        gps_running.drive(lon_s, lat_s, thd_distance=3, t_adj_gps=60)
        print("第3エリアです")
    elif count == 4:
        # condition =1
        # while condition == 1:
        #     if data_dist_bulearea4['distance']<=5:
        #         print("第"+count+"エリア到着")
        #         condition =0
        #     print("第"+count+"エリア外です")
        gps_running.drive(lon_w, lat_w, thd_distance=3, t_adj_gps=60)
        print("第4エリアです")
    else:
        print("青点エリア捜索終了")
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
    #画像伝送
    # latest_picture_path = None

    #人の座標
    #グランドの中央
    lat_human = 35.9243068
    lon_human = 139.9124594
    #中庭
    #lat_human =35.918329 
    #lon_human =139.907841

    #ゴール座標
    #グランドのゴール前
    lat_goal = 35.9242411
    lon_goal = 139.9120618
    #中庭
    #lat_goal = 35.918329
    #lon_goal = 139.907841
 
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
            send.send_data("Release")
            break
        else:
            print('unfulfilled')
            send.send_data("judging")
    other.log(log_release, "release judge finish")
    send.send_data("release finish")
    print("release finish!!!")
    ###-------land judge -------###
    print("START: Land judge")
    other.log(log_phase,'3',"land phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)

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
            send.send_data("landed")
            print('##--landed--##')
            break
        else:
            print('Press unfulfilled')
            send.send_data("judging")
    other.log(log_landing, "land judge finish")
    send.send_data("land finish")
    time.sleep(3)
    print("land finish!!!")
    send.send_reset(t_reset = 5)
    ###-------melt-------###

    print("START: Melt")
    other.log(log_phase,'4',"melt phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    pi = pigpio.pi()

    meltPin = 4
    other.log(log_melting, datetime.datetime.now(), time.time() - t_start,  "melt start")
    try:
        melt.down()
        send.send_data("melting")
    except:
        pi.write(meltPin, 0)

    other.log(log_melting, datetime.datetime.now(), time.time() - t_start,  "melt finish")
    send.send_data("melt finish")
    print("melt finish!!!")

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
    send.send_data("paraavo finish")
    time.sleep(3)

    print("paraavo finish!!!")
######--------------run1--------------######
    print("START:gps running1")
    other.log(log_phase,'6',"gps running1 phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)

    other.log(log_gpsrunning1,"run1 start")
    goal_distance = gps_running.drive(lon_human, lat_human, thd_distance=5, t_adj_gps=60,logpath=log_gpsrunning1)
    print(f'-----distance: {goal_distance}-----')
    other.log(log_gpsrunning1,"run1 finish")
    send.send_data("run1 finish")
    print("finish!")
    motor.motor_stop(1)
    send.send_reset(t_reset=5)
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
            motor.move(20, -20, 0.25) #グランド
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
                move_to_bulearea(count, lat_human, lon_human)
                human_judge_count, break_outer_loop = take_and_rotation(human_judge_count=human_judge_count, break_outer_loop=break_outer_loop,logpath=log_humandetect, model=ML_people)
    if human_judge_count==3:
        motor.move(-20, 20, 0.25)
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
                        send_lat = "{:.6f}".format(lat)
                        send_lon = "{:.6f}".format(lon)
                        print(send_lat,send_lon)
                    # 無線で送信
                        time.sleep(delay)
                        send.send_data("human_GPS_start")
                        print("human_GPS_start")
                        time.sleep(delay)
                        send.send_data(send_lat)
                        send.send_data(send_lon)
                        print(lat,lon)
                        time.sleep(delay)
                        send.send_data("human_GPS_fin")
                        print("human_GPS_fin")
                        time.sleep (delay)
                        break
                time.sleep(1)
            except KeyboardInterrupt:
                gps.close_gps()
                print("\r\nKeyboard Intruppted, Serial Closed")
            except:
                gps.close_gps()
                print(traceback.format_exc())
        
    #---------------------画像伝送----------------------------#
    
        time.sleep(15)
        #file_path = latest_picture_path
        file_name = "/home/dendenmushi/cansat2023/sequence/ML_imgs/jpg"  # 保存するファイル名を指定
        photo_take = take.picture(file_name, 320, 240)
        print("撮影した写真のファイルパス：", photo_take)
        
        # 入力ファイルパスと出力ファイルパスを指定してリサイズ
        input_file = photo_take     # 入力ファイルのパスを適切に指定してください
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
                if id_counter%30==0:
                    time.sleep(10)
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
        time.sleep(10)
        
        end_time = time.time()  # プログラム終了時刻を記録
        execution_time = end_time - start_time  # 実行時間を計算
        
        print("実行時間:", execution_time, "秒")
        print("データを", output_filename, "に保存しました。")            
    other.log(log_humandetect,"humandetect finish")
    send.send_data("human finish")
    print("human detection finish!!!")
######--------------run2--------------######
    other.log(log_phase,'8',"gps running2 phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    other.log(log_gpsrunning2,"run2 start")
    gps_running.drive(lon_goal, lat_goal, thd_distance=10, t_adj_gps=50,logpath=log_gpsrunning2)
    print(f'-----distance: {goal_distance}-----')
    other.log(log_gpsrunning2,"run2 finish")
    send.send_data("run2 finish")
    print("finish!")
    motor.motor_stop(1)
######--------------goal--------------######
    other.log(log_phase,'9',"goal phase",datetime.datetime.now(),time.time()-t_start)
    phase=other.phase(log_phase)
    other.log(log_photorunning,"photorun start")
    while True:
        try:
            angle = 0
            t_running = 0

            area_ratio, angle = imgguide.detect_goal(lat_goal, lon_goal)
            imgguide.image_guided_driving(area_ratio, angle, lat_goal, lon_goal)
            break
        except:
            print("restarting photo running")

#------ゴール終了-----#

    other.log(log_photorunning,"photorun finish")
    print("photorun finish")
    other.log(log_phase,'10',"all phase complete",datetime.datetime.now(),time.time()-t_start)
    print("all complete!")