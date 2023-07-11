#上書き保存されないようにするために、ファイル名を日付にする
import datetime
import cv2

dt_now = datetime.datetime.now()
print(dt_now)

def save_img(save_img_path, img_name, save_img):
    dt_now = datetime.datetime.now()
    final_name = save_img_path + img_name + str(dt_now) + ".jpg"
    cv2.imwrite(final_name, save_img)

if __name__ == '__main__':