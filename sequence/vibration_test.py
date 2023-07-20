import bmx055
import bme280
import gps
import time
import pigpio
from smbus import SMBus
import smbus
import logging
import other
import motor
import send
import melt
import land

def vib_test():
    logpath = other.filename('./log/vibration_test/vibration_test_log','txt')

    #-----3分のマージン-----#
    print("vibration test start")
    print("wait 3mins")
    time.sleep(180)

    #-----着地判定-----#
    print("land detect start")
    send.send_data("TXDU 0001,0000")

    landcount = 0
    pressdata = [0.0, 0.0, 0.0, 0.0]

    while True:
        presslandjudge = 0
        landcount, presslandjudge = land.pressdetect_land(0.1)
        print(f'count:{landcount}\tjudge:{presslandjudge}')
        if presslandjudge == 1:
            print('Press')
            send.send_data("TXDU 0001,1000")
            print('##--landed--##')
            send.send_data("TXDU 0001,1111")
            break
        else:
            print('Press unfulfilled')
            send.send_data("TXDU 0001,0001")

    #-----溶断回路-----#
    print("melt start")
    other.log(logpath, "melt start")
    meltPin = 4
    try:
        melt.down()
    except:
        pi.write(meltPin, 0)

    print("melt finish")
    other.log(logpath, "melt finish")

    #2秒スリープ
    time.sleep(2)

    #-----少しだけ前進-----#
    motor.move(35, 35, 0.05)
    other.log(logpath, "move forward")

    #-----data read-----#

    #-----logのヘッダー-----#
    other.log(logpath, 'accx',  'accy', 'accz', 'gyrx', 'gyry', 'gyrz', 'magx', 'magy', 'magz', 'temp', 'press', 'hum', 'alt', 'utc', 'lat', 'lon', 'sHeight', 'gHeight')

    try:
        gps.open_gps()
        t_start = time.time()
        while True:
            accx, accy, accz, gyrx, gyry, gyrz, magx, magy, magz  = bmx055.bmx055_read()
            print("-----bmx055 data-----")
            print(accx, accy, accz, gyrx, gyry, gyrz, magx, magy, magz)
            print("-----bme280 data-----")
            temp, press, hum, alt = bme280.bme280_read()
            print(temp, press, hum, alt)
            print("-----gps data-----")
            utc, lat, lon, sHeight, gHeight = gps.read_gps()
            if utc == -1.0:
                if lat == -1.0:
                    print("Reading gps Error")
                    # pass
                else:
                    # pass
                    print("Status V")
            else:
                # pass
                print(utc, lat, lon, sHeight, gHeight)

            print("----------")

            #ログの保存
            other.log(logpath, accx, accy, accz, gyrx, gyry, gyrz, magx, magy, magz, temp, press, hum, alt, utc, lat, lon, sHeight, gHeight)

            time.sleep(1)

    except KeyboardInterrupt:
        gps.close_gps()
        print("\r\n")
    except Exception as e:
        gps.close_gps()
        print(e.message())
    

if __name__ == '__main__':
    #セットアップ
    bmx055.bmx055_setup()
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    gps.open_gps()
    motor.setup()

    #-----振動試験-----#
    vib_test()