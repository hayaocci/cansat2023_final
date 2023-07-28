import time
from machine_learning import DetectPeople
import human_detection
import take
import other
import machine_learning
log_humandetect=other.filename('/home/dendenmushi/cansat2023/sequence/log/humandetectlog','txt')



if __name__=='__main__':
    print("START:human detect")
    count = 0
    human_judge_count=0
    break_outer_loop =False
    start_time = time.time()
    threshold = 20 * 60
    elapsed_time = time.time()-start_time
    
    ML_people = DetectPeople(model_path="model_mobile.tflite" )

    # lat_n, lon_n, lat_e, lon_e, lat_s, lon_s, lat_w, lon_w = human_detection.get_locations(lat_human, lon_human)
    
   
    #まずはメインエリアを捜索
    for k in range(3):
        if break_outer_loop == False:
            human_judge_count = 0
            #撮影
            img_path = take.picture('ML_imgs/image', 320, 240)
            
            #モデルの読み込み
            result = ML_people.predict(image_path=img_path)
            

            #hitoの確率80%かどうか
            if result >= 0.80:
                human_judge_count += 1
                # 追加の写真を撮影
                for h in range(2):
                    additional_img_path = take.picture('ML_imgs/additional_image', 320, 240)
                    additional_result = ML_people.predict(image_path=additional_img_path)
                   
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
            #motor.move(20, -20, 0.2) #グランド
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
                #lat_now, lon_now = gps.location()
                count += 1
                #human_detection.move_to_bulearea(count, lat_human, lon_human)
                human_judge_count, break_outer_loop = human_detection.take_and_rotation(human_judge_count=human_judge_count, break_outer_loop=break_outer_loop,logpath=log_humandetect)