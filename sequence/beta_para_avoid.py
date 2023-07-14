#パラシュート回避
import wgps_beta_photo_running as photo_running
import cv2
from save_photo import save_img
import take
import motor

def detect_para():
    #画像の撮影
    path_all_para = '/home/dendenmushi/cansat2023/sequence/photo_storage/para_all/para_detect-'
    path_para_detect = './photo_storage/para_detected'
    photoname = take.picture(path_all_para)
    para_img = cv2.imread(photoname)
    angle = 0

    #画像を圧縮
    small_img = photo_running.mosaic(para_img, ratio=0.8)

    #赤色であると認識させる範囲の設定
    mask, masked_img = photo_running.detect_red(small_img)

    #圧縮した画像から重心と輪郭を求めて、画像に反映
    para_img, max_contour, cx, cy = photo_running.get_center(mask, small_img)

    #赤色が占める割合を求める
    red_area = photo_running.get_area_test(max_contour, para_img)

    #重心の位置から現在位置とパラシュートと相対角度を大まかに計算
    angle = photo_running.get_angle(cx, cy, para_img)

    if red_area == 0:
        angle = 0

    #パラシュートが検出された場合に画像を保存
    if red_area != 0:
        red_area = int(red_area)
        save_img(path_para_detect, 'para_detected_' + str(red_area), "a" ,para_img)
    
    return red_area, angle

def para_avoid(red_area, angle, thd_para_avoid=0, thd_para_count=4):
    #thd_para_avoidはパラシュートがあると判定する割合の閾値
    #thd_para_countはパラシュートがないとき何回確認するかの閾値
    pwr = 30
    check_count = 0
    while 1:
        red_area, angle = detect_para()
        while red_area > thd_para_avoid and check_count <= thd_para_count:
            if check_count == thd_para_count:
                break
            
            if angle == 1:
                motor.move(pwr, -pwr, 0.2)
            elif angle == 2:
                motor.move(pwr, -pwr, 0.3)
            elif angle == 3:
                motor.move(pwr, -pwr, 0.4)
            elif angle == 4:
                motor.move(-pwr, pwr, 0.3)
            elif angle == 5:
                motor.move(-pwr, pwr, 0.2)
            #elif red_area == 0 or angle == 0:
            else:
                i = 1 + check_count
                print("パラシュートはありません。確認" + str(i) + "回目です。")

            check_count += 1

            red_area, angle = detect_para()
        else:
            print("確認しました。パラシュートはありません。")
            print("直進します。")
            red_area, angle = detect_para()
            break

    #パラシュートが前方にないことが確認できたので、直進する。
    if red_area == 0 and check_count == thd_para_count:
        pwr_st = 40
        motor.move(pwr_st, pwr_st, 2)
        print("パラシュートは回避できました。")

if __name__ == '__main__':
    #セットアップ
    motor.setup()

    red_area, angle = detect_para()
    para_avoid(red_area, angle)