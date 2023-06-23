import gps_navigate
import time 
import rotation
import machine_learning
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



if __name__ =="__main__":

    start_time = time.time()
    threshold = 20 * 60
    elapsed_time = time.time()-start_time

    lat1 = 35.12345
    lon1 = 139.67890

    lat2_b, lon2_b, lat3_b, lon3_b, lat4_b, lon4_b, lat5_b, lon5_b = calculate_square_corners(lon1, lat1)


    #6回繰り返すところへ
    for i in range(6):
        result=machine_learning.pro_people()
        #hitoの確率50%かどうか
        if result >=0.50:
            print("A")#対象に近づいて終了へ
        else:
            if elapsed_time >= threshold:#20分経ったか
             print("A")#終了へ行くように変更して
            else:
                print("捜索続けます")
        rotation()#プログラム要変更

    #青点に移動する
    gps_running1.drive(lon2_b, lat2_b, thd_distance=10, t_adj_gps=60)
    
    def distance_bluearea1(lat2_b,lon2_b):#ここちょっと分からん
        data_dist_bulearea1 =gps_navigate.vincenty_inverse(lat_now,lon_now,lat2_b,lon2_b)
        #青点から5m以内か
        if data_dist_bulearea1['distance']<=5:
            print("第2捜索地点到達")
            #「6回繰り返すところへ」に移動したい
        else:
            print("B")#「青点に移動する」にループしたい

    #↑これをbulearea1~4まで繰り返したい
    

