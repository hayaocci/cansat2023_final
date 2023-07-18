import bmx055
import bme280
import gps
import time
import pigpio
from smbus import SMBus
import smbus
import logging
from other import log

bmx055.bmx055_setup()
bme280.bme280_setup()
bme280.bme280_calib_param()

try:
    gps.open_gps()
    t_start = time.time()
    while True:
        bmxData = bmx055.bmx055_read()
        print("-----bmx055 data-----")
        print(bmxData)
        log('./log/vibration_test/', bmxData)
        print("-----bme280 data-----")
        temp,pres,hum,alt = bme280.bme280_read()
        print(str(pres) + "\t" + str(alt) + "\t" + str(temp) + "\t" + str(hum))
        log
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
        time.sleep(1)

except KeyboardInterrupt:
    gps.close_gps()
    print("\r\n")
except Exception as e:
    gps.close_gps()
    print(e.message())