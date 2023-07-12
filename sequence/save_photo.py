#上書き保存されないようにするために、ファイル名を日付にする
import datetime
import cv2

def save_img(img_path, img_name, img):
    #日時の取得
    dt_now = datetime.datetime.now()
    dt_name = str(dt_now.strftime('%Y%m%d_%H%M%S'))
    final_img_path = img_path + "/" + img_name + + '_' + dt_name + ".jpg"

    #画像の保存
    cv2.imwrite(final_img_path, img)

    print("photo_saved")