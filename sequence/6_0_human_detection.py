import gps_navigate
import time
import traceback

#人検出の範囲内にいるかいないかの判定

def distance_human(lat1, lon1, lat2, lon2):
    data_dist_human = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
    try:
        data_dist_human['distance'] <= 20
        print("人検出の範囲内にいます")


    except:
        print("人検出の範囲外にいます")

        print_im920sl(str(data_dist_human['distance']) + '----!!!    human   !!!')
        return False




