import gps_navigate
import time 
#import rotation
import machine_learning
from machine_learning import DetectPeople
import gps_running1
import take
import gps
from math import sqrt
import motor

'''
#chatGPTさんより青点の設定
#lon1,lat1は赤点の位置
def calculate_square_corners(lon1, lat1):
    # 1度あたりの緯度経度の差（おおよその値）
    lat_diff_per_meter = 0.000009
    lon_diff_per_meter = 0.000011

    # 正方形の一辺の長さ（メートル）
    square_side_length = 20

    # 正方形の角の座標を計算
    lon_n = lon1 + (square_side_length / 2) * lon_diff_per_meter
    lat_n = lat1 - (square_side_length / 2) * lat_diff_per_meter

    lon_e = lon1 + (square_side_length / 2) * lon_diff_per_meter
    lat_e = lat1 + (square_side_length / 2) * lat_diff_per_meter

    lon_s = lon1 - (square_side_length / 2) * lon_diff_per_meter
    lat_s = lat1 - (square_side_length / 2) * lat_diff_per_meter

    lon_w = lon1 - (square_side_length / 2) * lon_diff_per_meter
    lat_w = lat1 + (square_side_length / 2) * lat_diff_per_meter

    return lat_n, lon_n, lat_e, lon_e, lat_s, lon_s, lat_w, lon_w
'''

#最後の位置情報をもとに周囲の4つの点の座標を求める
def get_locations(lat_human, lon_human):
    #北緯40度における10mあたりの緯度経度の差
    #緯度は0.3236246秒　経度は0.3242秒
    #lat_dif = 0.0000323
    #lon_dif = 0.0000324

    lat_dif = 0.0000090
    lon_dif = 0.0000117
    
    #捜索エリアの1辺の長さ
    side_length = 20

    #周囲の4つの位置を求める
    #north
    lat_n = lat_human + lat_dif*(side_length/2)
    lon_n = lon_human
    #east
    lat_e = lat_human
    lon_e = lon_human - lon_dif*(side_length/2)
    #south
    lat_s = lat_human - lat_dif*(side_length/2)
    lon_s = lon_human
    #west
    lat_w = lat_human
    lon_w = lon_human + lon_dif*(side_length/2)

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

def take_and_rotation(break_outer_loop):
    for i in range(6):
        img_path = take.picture('ML_imgs/image', 320, 240)
        
        result = ML_people.predict(image_path=img_path)
        # result=machine_learning.pro_people()
        #hitoの確率50%かどうか
        if result >=0.50:
            print("遭難者発見")
            break_outer_loop = True
            break
        else:
            if elapsed_time >= threshold:#20分経ったか
                break_outer_loop = True
                break
            else:
                print("捜索続けます")
        #rotation() 
        motor.motor_move(10, -10, 0.5)
    print("6回撮影しました")
    print("次のエリアに移動します")
    return break_outer_loop
    
def move_to_bulearea(count):
 
    data_dist_bulearea1 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat_n,lon_n)
    data_dist_bulearea2 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat_e,lon_e)
    data_dist_bulearea3 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat_s,lon_s)
    data_dist_bulearea4 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat_w,lon_w)
    
    count += 1
    #青点から5m以内か
    if count == 1:
        condition =1
        while condition == 1:
            if data_dist_bulearea1['distance']<=5:
                print("第"+count+"エリア到着")
                condition =0
            print("第"+count+"エリア外です")
            gps_running1.drive(lon_n, lat_n, thd_distance=10, t_adj_gps=60)
    elif count == 2:
        condition =1
        while condition == 1:
            if data_dist_bulearea2['distance']<=5:
                print("第"+count+"エリア到着")
                condition =0
            print("第"+count+"エリア外です")
            gps_running1.drive(lon_e, lat_e, thd_distance=10, t_adj_gps=60)   
    elif count == 3:
        condition =1
        while condition == 1:
            if data_dist_bulearea3['distance']<=5:
                print("第"+count+"エリア到着")
                condition =0
            print("第"+count+"エリア外です")
            gps_running1.drive(lon_s, lat_s, thd_distance=10, t_adj_gps=60)
    elif count == 4:
        condition =1
        while condition == 1:
            if data_dist_bulearea4['distance']<=5:
                print("第"+count+"エリア到着")
                condition =0
            print("第"+count+"エリア外です")
            gps_running1.drive(lon_w, lat_w, thd_distance=10, t_adj_gps=60)
    else:
        print("青点エリア捜索終了")             
    
if __name__ =="__main__":

    count = 0
    break_outer_loop =False
    start_time = time.time()
    threshold = 20 * 60
    elapsed_time = time.time()-start_time
    #lat1 = 35.12345 #赤点
    #lon1 = 139.67890 #赤点

    #12号館前
    lat_human = 35.91896917
    lon_human = 139.90859362

    ML_people = DetectPeople(model_path="model_mobile.tflite" )

    lat_n, lon_n, lat_e, lon_e, lat_s, lon_s, lat_w, lon_w = get_locations(lat_human, lon_human)

    for j in range(4):
        elapsed_time = time.time()-start_time #経過時間の更新
        if break_outer_loop:
            break
        lat_now, lon_now = gps.location()
        move_to_bulearea()
        take_and_rotation()
    
