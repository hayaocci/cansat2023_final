import tensorflow.lite as tflite
import numpy as np
from PIL import Image
import cv2

# モデルの読み込み
interpreter = tflite.Interpreter(model_path="model_mobile.tflite")
interpreter.allocate_tensors()


# 入力と出力テンソルの情報を取得
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


# 予測対象の画像を読み込む
image_path = "test.JPG"
image = cv2.imread(image_path)
pix = 224


# 画像の前処理
image = cv2.resize(image, (pix, pix))
image = np.array(image) / 255.0
image = np.expand_dims(image, axis=0)


# 入力データのセットアップ
input_data = image.astype(np.float32)
interpreter.set_tensor(input_details[0]['index'], input_data)

# 推論の実行
interpreter.invoke()


# 出力データの取得
output_data = interpreter.get_tensor(output_details[0]['index'])


# 予測結果の処理
predicted_class = np.argmax(output_data, axis=1)
class_names = ["hito", "other"]
predicted_label = class_names[predicted_class[0]]


print("予測結果:", predicted_label)
