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
    time.sleep(2)

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
    meltPin = 4
    try:
        melt.down()
    except:
        pi.write(meltPin, 0)

    print("melt finish")

    #2秒スリープ
    time.sleep(2)

    #-----少しだけ前進-----#
    motor.move(40, 40, 0.05)

    #-----data read-----#
    try:
        gps.open_gps()
        t_start = time.time()
        while True:
            bmxData = bmx055.bmx055_read()
            print("-----bmx055 data-----")
            print(bmxData)
            print("-----bme280 data-----")
            bmeData = bme280.bme280_read()
            print(bmeData)
            print("-----gps data-----")
            gpsData = gps.read_gps()
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
            try:
                for i in range(len(bmxData)):
                    if bmxData[i] is None:
                        bmxData[i] = round(bmxData[i], 4)
                        bmxData[i] = '{:.4f}'.format(bmxData[i]) #0埋め追加

                for n in range(len(bmeData)):
                        if bmeData[n] is None:
                            bmeData[n] = round(bmeData[n], 4)
                            bmeData[n] = '{:.4f}'.format(bmeData[n]) #0埋め追加
                
                for l in range(len(gpsData)):
                    if gpsData[l] is None:
                        gpsData[l] = round(gpsData[l], 8)
                        gpsData[l] = '{:.8f}'.format(gpsData[l])

            except:
                bmxData = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                bmeData = [0.0, 0.0, 0.0, 0.0]
                gpsData = [0.0, 0.0, 0.0, 0.0, 0.0]
                



            other.log(logpath, bmxData, temp, pres, hum, alt, utc, lat, lon, sHeight, gHeight)

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