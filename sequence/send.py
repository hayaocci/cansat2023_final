import serial
import time

def send_data(data, port='/dev/ttyS0', baudrate=19200):
    IM920Serial = serial.Serial(port, baudrate)
    IM920Serial.flushOutput()
    IM920Serial.write((data + '\r\n').encode())
    IM920Serial.close()

if __name__ == '__main__':
    send_data("TXDU 0001,ABCD")
    print('送信しました')
