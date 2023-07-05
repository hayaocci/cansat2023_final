import serial
import time

def send_data(data, port='/dev/ttyAMA0', baudrate=19200):
    IM920Serial = serial.Serial(port, baudrate)
    IM920Serial.flushOutput()
    IM920Serial.write((data + '\r\n').encode())
    IM920Serial.close()

if __name__ == '__main__':
    IM920Serial = serial.Serial('/dev/ttyAMA0', baudrate=19200)
    IM920Serial.flushOutput()
    IM920Serial.write(("TXDU 0001,こんにちは" + '\r\n').encode())
    IM920Serial.close()
    print('送信しました')
