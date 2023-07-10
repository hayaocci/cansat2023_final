import serial
import time

def send_data(data, port='/dev/ttyAMA0', baudrate=19200):
    IM920Serial = serial.Serial(port, baudrate)
    IM920Serial.flushOutput()
    IM920Serial.write((data + '\r\n').encode())
    IM920Serial.close()

def receive_data(port='/dev/ttyAMA0', baudrate=19200):
    IM920Serial = serial.Serial(port, baudrate)
    IM920Serial.flushInput()
    received_data = IM920Serial.readline().strip()
    IM920Serial.close()
    return received_data

if __name__ == '__main__':
    print("無線の初期設定")
    text = input("送信するデータを入力してください: ")
    send_data(text)
    time.sleep(1)
    received_data = receive_data()
    print("受信データ:", received_data)

