import time
import gps_navigate
from machine_learning import DetectPeople
import take


if __name__ == "__main__":
#人検出の範囲内にいるかいないかの判定
    def distance_human(lat1, lon1, lat2, lon2):
        data_dist_human = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
        
        if data_dist_human['distance'] <= 20:
            print("人検出の範囲内にいます")
            
            #人検知の処理
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

            return 



