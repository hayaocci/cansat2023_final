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

    #画像を圧縮
    small_img = photo_running.mosaic(para_img, ratio=0.1)

    #赤色であると認識させる範囲の設定
    mask, masked_img = photo_running.detect_red(small_img)

    #圧縮した画像から重心と輪郭を求めて、画像に反映
    para_img, max_contour, cx, cy = photo_running.get_center(mask, small_img)

    #赤色が占める割合を求める
    area_ratio = photo_running.get_area_test(max_contour, para_img)

    #重心の位置から現在位置とパラシュートと相対角度を大まかに計算
    angle = photo_running.get_angle(cx, cy, para_img)

    #パラシュートが検出された場合に画像を保存
    if area_ratio != 0:
        area_ratio = int(area_ratio)
        save_img(path_para_detect, 'para_detected_' + str(area_ratio), "a" ,para_img)
    
    return area_ratio, angle

def para_avoid(area_ratio, angle, thd_para_avoid=0.0, thd_para_count=4):
    #thd_para_avoidはパラシュートがあると判定する割合の閾値
    #thd_para_countはパラシュートがないとき何回確認するかの閾値
    pwr = 30
    check_count = 0
    while 1:
        area_ratio, angle = detect_para()
        while area_ratio > thd_para_avoid and check_count <= thd_para_count:
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
            elif area_ratio == 0:
                i = 1 + check_count
                print("パラシュートはありません。確認" + str(i) + "回目です。")

            check_count += 1

            area_ratio, angle = detect_para()
        else:
            print("3回確認しました。パラシュートはありません。")
            print("直進します。")
            break

    #パラシュートが前方にないことが確認できたので、直進する。
    pwr_st = 40
    motor.move(pwr_st, pwr_st, 2)
    print("パラシュートは回避できました。")

if __name__ == '__main__':
    #セットアップ
    motor.setup()

    area_ratio, angle = detect_para()
    para_avoid(area_ratio, angle)