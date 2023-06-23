import gps_navigate
import time
import traceback
import take

#人検出の範囲内にいるかいないかの判定

def distance_human(lat1, lon1, lat2, lon2):
    data_dist_human = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
    
    if data_dist_human['distance'] <= 20:
        print("人検出の範囲内にいます")
        


    else:
        print("人検出の範囲外にいます")
        return False
       




