import gps_navigate
import time 
import rotation
import machine_learning
import gps_running1
import take
from math import sqrt

#chatGPTさんより青点の設定
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

    

    if elapsed_time >= threshold:
        print("A")#終了へ行くように変更して
    else:
        #6回繰り返すところへ
        for i in range(6):
            take()
            DetectPeople()#人検知を行いたい、要変更
            rotation()
        result=machine_learning.pro_people()
        #hitoの確率50%かどうか
        if result >=0.50:
            print("A")#対象に近づく
        else:
            print("B")#もう一回遊べるドン
        #青点に移動する
        gps_running1.drive(lon2_b, lat2_b, thd_distance=10, t_adj_gps=60)

        #青点からxm以内であるか
        if :
        else:

