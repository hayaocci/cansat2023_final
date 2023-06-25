#0623 作成開始　by田口
#人検知プログラム

#モデュールのインポート　（一時敵にコメントアウトしてる）
import time
import gps_navigate
from machine_learning import DetectPeople
#import take

#サンプルデータ
lat1 = 35.9192167
lon1 = 139.9081122
lat2 = 35.9182190
lon2 = 139.9181130



if __name__ == "__main__":
#人検出の範囲内にいるかいないかの判定
    data_distance_human = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
    print(data_distance_human)

    if data_distance_human['distance'] <= 20:
        print("人検知の範囲内にいます")
        print("人検知モードに入ります")
        ML_people = DetectPeople(model_path="model_mobile.tflite" )
        # image_path = 'imgs/hiroyuki.jpg'
        # image_path = 'imgs/saru.jpg'
        # ML_people.predict(image_path)
        while 1:
            img_path = take.picture('ML_imgs/image', 320, 240)
            ML_people.predict(image_path=img_path)


    else:
        print("人検知の範囲外にいます")
        print("人検知の範囲内に移動してください")
        #人検知の範囲外にいる場合は、移動するように指示をする

    '''
    def distance_human(lat1, lon1, lat2, lon2):
        data_dist_human = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
        
        
        if data_dist_human['distance'] <= 20:
            print("人検出の範囲内にいます")
            
            #人検知の処理(machine_learning.pyからコピペした)
            ML_people = DetectPeople(model_path="model_mobile.tflite" )
            # image_path = 'imgs/hiroyuki.jpg'
            # image_path = 'imgs/saru.jpg'
            # ML_people.predict(image_path)
            while 1:
                img_path = take.picture('ML_imgs/image', 320, 240)
                ML_people.predict(image_path=img_path)
                # time.sleep(3)
            

        else:
            print("人検出の範囲外にいます")
            #人検出の範囲外にいる場合は、人検出の範囲内に入るまで、ループする
        '''



