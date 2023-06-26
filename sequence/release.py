import time
import bme280
#from other import print

def pressdetect_release(thd_press_release, t_delta_release):
    '''
    気圧による放出判定
    '''
    global press_count_release
    global press_judge_release
    try:
        pressdata = bme280.bme280_read()
        prevpress = pressdata[1]
        time.sleep(t_delta_release)
        pressdata = bme280.bme280_read()
        latestpress = pressdata[1]
        deltP = latestpress - prevpress
        if 0.0 in pressdata:
            print("##--bme280rror!--##")
            press_count_release = 0
            press_judge_release = 2
        elif deltP > thd_press_release:
            press_count_release += 1
            if press_count_release > 1:
                press_judge_release = 1
                print("##--pressreleasejudge--##")
        else:
            press_count_release = 0
            press_judge_release = 0
    except KeyboardInterrupt:
        print('pressdetect_release_Interrupt')
        exit()
    except:
        press_count_release = 0
        press_judge_release = 2
    return press_count_release, press_judge_release


if __name__ == "__main__":
    thd_press_release = 0.3
    pressreleasecount = 0
    pressreleasejudge = 0
    t_delta_release = 3
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    press_d = 0

    while press_d <= 3:
        press_count_release, press_judge_release = pressdetect_release(thd_press_release, t_delta_release)
        print(f'count:{pressreleasecount}\tjudge{pressreleasejudge}')
        if pressreleasejudge == 1:
            print('Press')
            press_d = press_d + 1
            
        else:
            print('unfulfilled')
    
    print('##--released--##')