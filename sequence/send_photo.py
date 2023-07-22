import time
from PIL import Image
import binascii
import base64
from jinja2 import Environment, FileSystemLoader
import math
import time
import pigpio
import numpy as np
import traceback
import send
import wireless_communication
import cv2

RX = 27
pi = pigpio.pi()
chunk_size = 8  # 1回に表示するバイト数
delay = 0.2  # 表示間隔（秒）

def capture_and_save_photo(file_name):
    # カメラを起動
    camera = cv2.VideoCapture(0)
    
    # カメラが正常にオープンされたか確認
    if not camera.isOpened():
        print("カメラをオープンできませんでした。")
        return
    
    # 画像を撮影
    ret, frame = camera.read()
    
    if not ret:
        print("画像の取得に失敗しました。")
        camera.release()
        return
    
    # 画像をファイルに保存
    cv2.imwrite(file_name, frame)
    print("写真が保存されました。")
    
    # カメラを解放
    camera.release()


def compress_image(image_path, output_path, quality):
    image = Image.open(image_path)
    image.save(output_path, optimize=True, quality=quality)


def image_file_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        data = base64.b64encode(image_file.read())

    return data.decode('utf-8')


#---------------------GPS情報送信--------------------------
#gps情報取得
wireless_communication.open_gps()

num_samples = 5
lat_sum = 0.0
lon_sum = 0.0

for _ in range(num_samples):
    lat, lon = wireless_communication.location()
    lat_sum += lat
    lon_sum += lon

# 平均計算
avg_lat = lat_sum / num_samples
avg_lon = lon_sum / num_samples

# 無線で送信
send.send_data("human_GPS_start")
time.sleep(delay)
send.sed_data(avg_lat,avg_lon)
time.sleep(delay)
send.send_data("human_GPS_fin")
time.sleep(delay)



#---------------------画像伝送-----------------------------

file_name = "/home/dendenmushi/cansat2023/sequence/ML_imgs/sendtest_photo.jpg"  # 保存するファイル名を指定
capture_and_save_photo(file_name)

# 圧縮したい画像のパスと出力先のパスを指定します
input_image_path = '/home/dendenmushi/cansat2023/sequence/ML_imgs/sendtest_photo.jpg'
compressed_image_path = 'compressed_test.jpg'

# 圧縮率を指定します（0から100の範囲の整数）
compression_quality = 50

# 画像を圧縮します
compress_image(input_image_path, compressed_image_path, compression_quality)

# 圧縮後の画像をバイナリ形式に変換します
with open(compressed_image_path, 'rb') as f:
    compressed_image_binary = f.read()


data = compressed_image_binary  # バイナリデータを指定してください
output_filename = "output.txt"  # 保存先のファイル名

start_time = time.time()  # プログラム開始時刻を記録

send.send_data ("wireless_start")

# バイナリデータを32バイトずつ表示し、ファイルに保存する
with open(output_filename, "w") as f:
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        chunk_str = "".join(format(byte, "02X") for byte in chunk)
        #chunk_strにデータがある
        print(chunk_str)
        send.send_data(chunk_str)
        # 表示間隔を待つ
        time.sleep(delay)

        # ファイルに書き込む
        f.write(chunk_str + "\n")

send.send_data ("wireless_fin")

end_time = time.time()  # プログラム終了時刻を記録
execution_time = end_time - start_time  # 実行時間を計算

print("実行時間:", execution_time, "秒")
print("データを", output_filename, "に保存しました。")
