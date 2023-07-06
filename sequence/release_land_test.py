import release
import land
import melt
import 
import time
import bme280
import pigpio
import send


if __name__  == "__main__":

    ###-------release judge -------###
    print("release judge start")
    thd_press_release = 0.1
    pressreleasecount = 0
    pressreleasejudge = 0
    t_delta_release = 10
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    press_d = 0

    while True:
        press_count_release, press_judge_release = release.pressdetect_release(thd_press_release, t_delta_release)
        print(f'count:{pressreleasecount}\tjudge{pressreleasejudge}')
        if press_count_release  > 3:
            print('Press')
            send.send_data("TXDU 0001.A001")
            break
        else:
            print('unfulfilled')
    send.send_data("TXDU 0001.A002")

    ###-------land judge -------###
    print("Start")
    send.send_data("TXDU 0001,B000")

    #bme280.bme280_setup()
    #bme280.bme280_calib_param()

    landcount = 0
    pressdata = [0.0, 0.0, 0.0, 0.0]

    while True:
        presslandjudge = 0
        landcount, presslandjudge = land.pressdetect_land(0.1)
        print(f'count:{landcount}\tjudge:{presslandjudge}')
        if presslandjudge == 1:
            print('Press')
            send.send_data("TXDU 0001,B002")
            print('##--landed--##')
            send.send_data("TXDU 0001,BBBB")
            break
        else:
            print('Press unfulfilled')
            send.send_data("TXDU 0001,B001")
    
    ###-------melt-------###

    pi = pigpio.pi()

    meltPin = 4
        try:
            melt.down()
            send.send_data("TXDU 0001,C001")
        except:
            pi.write(meltPin, 0)
    
    send.send_data("TXDU 0001,B001")
    ###------paraavo-------###

    

