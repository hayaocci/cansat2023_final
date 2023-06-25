import gps_navigate
import time 
import rotation
import machine_learning
from machine_learning import DetectPeople
import gps_running1
import take
from math import sqrt

#chatGPTさんより青点の設定
#lon1,lat1は赤点の位置
def calculate_square_corners(lon1, lat1):
    # 1度あたりの緯度経度の差（おおよその値）
    lat_diff_per_meter = 0.000009
    lon_diff_per_meter = 0.000011

    # 正方形の一辺の長さ（メートル）
    square_side_length = 20

    # 正方形の角の座標を計算
    lon2_b = lon1 + (square_side_length / 2) * lon_diff_per_meter
    lat2_b = lat1 - (square_side_length / 2) * lat_diff_per_meter

    lon3_b = lon1 + (square_side_length / 2) * lon_diff_per_meter
    lat3_b = lat1 + (square_side_length / 2) * lat_diff_per_meter

    lon4_b = lon1 - (square_side_length / 2) * lon_diff_per_meter
    lat4_b = lat1 - (square_side_length / 2) * lat_diff_per_meter

    lon5_b = lon1 - (square_side_length / 2) * lon_diff_per_meter
    lat5_b = lat1 + (square_side_length / 2) * lat_diff_per_meter

    return lat2_b, lon2_b, lat3_b, lon3_b, lat4_b, lon4_b, lat5_b, lon5_b







def take_and_rotation():
    for i in range(6):
        img_path = take.picture('ML_imgs/image', 320, 240)
        ML_people = DetectPeople(model_path="model_mobile.tflite" )
        ML_people.predict(image_path=img_path)
        result=machine_learning.pro_people()
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
        rotation()#プログラム要変更
    print("6回撮影しました")
    print("次のエリアに移動します")
    
def move_to_bulearea():
 
    data_dist_bulearea1 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat2_b,lon2_b)
    data_dist_bulearea2 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat3_b,lon3_b)
    data_dist_bulearea3 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat4_b,lon4_b)
    data_dist_bulearea4 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat5_b,lon5_b)
    
    count += 1
    #青点から5m以内か
    if count == 1:
        condition =1
        while condition == 1:
            if data_dist_bulearea1['distance']<=5:
                print("第"+count+"エリア到着")
                condition =0
            print("第"+count+"エリア外です")
            gps_running1.drive(lon2_b, lat2_b, thd_distance=10, t_adj_gps=60)
    elif count == 2:
        condition =1
        while condition == 1:
            if data_dist_bulearea2['distance']<=5:
                print("第"+count+"エリア到着")
                condition =0
            print("第"+count+"エリア外です")
            gps_running1.drive(lon3_b, lat3_b, thd_distance=10, t_adj_gps=60)   
    elif count == 3:
        condition =1
        while condition == 1:
            if data_dist_bulearea3['distance']<=5:
                print("第"+count+"エリア到着")
                condition =0
            print("第"+count+"エリア外です")
            gps_running1.drive(lon4_b, lat4_b, thd_distance=10, t_adj_gps=60)
    elif count == 4:
        condition =1
        while condition == 1:
            if data_dist_bulearea4['distance']<=5:
                print("第"+count+"エリア到着")
                condition =0
            print("第"+count+"エリア外です")
            gps_running1.drive(lon5_b, lat5_b, thd_distance=10, t_adj_gps=60)
    else:
        print("青点エリア捜索終了")             
    
if __name__ =="__main__":

    count = 0
    break_outer_loop = False
    start_time = time.time()
    threshold = 20 * 60
    elapsed_time = time.time()-start_time
    lat1 = 35.12345
    lon1 = 139.67890

    lat2_b, lon2_b, lat3_b, lon3_b, lat4_b, lon4_b, lat5_b, lon5_b = calculate_square_corners(lon1, lat1)

    for j in range(4):
        if break_outer_loop:
            break
        move_to_bulearea()
        take_and_rotation()
    
