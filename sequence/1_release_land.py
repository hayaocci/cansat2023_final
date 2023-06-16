import sys
sys.path.append('/home/cansat2023/sequence/bme280') 
from gps import gps_data_read
import bme280 
import time
import signal


def pressdetect_release(thd_press_release, t_delta_release):
    global press_count_release
    global press_judge_release
    try:
        pressdata = bme280.bme280_read()
        prevpress = pressdata[1]
        time.sleep(t_delta_release) #５秒待って次の気圧の値を読むよ
        pressdata = bme280.bme280_read()
        latestpress = pressdata[1]
        deltP = latestpress - prevpress #初めにとった気圧-後にとった気圧
        if 0.0 in pressdata:
            print("bme280error!")
            press_judge_release = 2
            press_count_release = 0
        elif deltP > thd_press_release:
            press_count_release += 1
            if press_count_release > 0:
                press_judge_release = 1
                print("pressreleasejudge")
        else:
            press_count_release = 0
            press_judge_release = 0
    except:
        press_count_release = 0
        press_judge_release = 2
    return press_count_release, press_judge_release


def pressdetect_land(anypress):
    """
    気圧情報による着地判定用
    引数はどのくらい気圧が変化したら判定にするかの閾値
    """
    global press_count_land
    global press_judge_land
    try:
        pressdata = bme280.bme280_read()
        Prevpress = pressdata[1]
        time.sleep(1) #1秒待って次の気圧の値を読むよ
        pressdata = bme280.bme280_read()
        Latestpress = pressdata[1]
        deltP = abs(Latestpress - Prevpress) #初めにとった気圧-後にとった気圧
        if 0.0 in pressdata:
            print("bme280error!")
            press_count_land = 0
            press_judge_land = 2
        elif deltP < anypress:
            press_count_land += 1
            if press_count_land > 5:
                press_judge_land = 1
                print("presslandjudge")
        else:
            press_count_land = 0
            press_judge_land = 0
    except:
        press_count_land = 0
        press_judge_land = 2
    return press_count_land, press_judge_land

def handle_interrupt(signal, frame):
    #キーボードの割り込み処理
    print("Interrupted")
    sys.exit(0)
    
def detect_landing(landing_threshold, landing_duration):
    landing_start_time = None

    while True:
        bmx_data = bmx055_read()
        acc_x, acc_y, acc_z = bmx_data[:3]

        # 加速度の変化が一定値以下であるか判定
        if abs(acc_x) < landing_threshold and abs(acc_y) < landing_threshold:
            # 着地判定の開始時刻を記録
            if landing_start_time is None:
                landing_start_time = time.time()
            # 着地判定の猶予期間を超えた場合、着地と判断
            elif time.time() - landing_start_time > landing_duration:
                print("着地しました")
                break
        else:
            # 加速度が閾値を超える場合、着地判定をリセット
            landing_start_time = None

        time.sleep(0.01)  # 適宜待機時間を調整

if __name__ == '__main__':
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    startTime = time.time()
    #放出判定用
    press_count_release = 0
    press_judge_release = 0
    #着地判定用
    press_count_land = 0
    press_judge_land = 0

    #キーボードの割り込みのシグナルハンドラを設定
    signal.signal(signal.SIGINT, handle_interrupt)

    #放出判定
    try:
        while 1:
            press_count_release, press_judge_release = pressdetect_release(0.3,0.5) 
            pressdate = bme280.bme280_read()
            print(f'count{press_count_release}\tjudge{press_judge_release}\ttemprature{pressdate[0]}\tpressure{pressdate[1]}')
            if press_judge_release == 1:
                print('release detected')
                break
    except KeyboardInterrupt:
        pass

    #着地判定
    try:
        while 1:
            press_count_land, press_judge_land = pressdetect_land(0.1) #閾値0.1
            # GPSの高度情報を取得
　　　　　　 utc, lat, lon, sHeight, gHeight = gps_data_read()
            print(f'count{press_count_land}\tjudge{press_judge_land}')
            if press_judge_land == 1:
                print('land detected')
                break
    except KeyboardInterrupt:
        pass

 # BMX055のセンサー値を使った着地判定
    threshold = 0.1  # 加速度の閾値（適宜調整）
    duration = 0.5  # 着地とみなす猶予期間（適宜調整）
    detect_landing(threshold, duration)

    print('finished')


    # try:
    #     while 1:
    #         presscount_release, pressjudge_release = pressdetect_release(0.3)
    #         print(f'count{presscount_release}\tjudge{pressjudge_release}')
    #         if pressjudge_release == 1:
    #             print('release detected')
    #             break
    #
    #     while 1:
    #         presscount_land, pressjudge_land = pressdetect_land(0.1)
    #         print(f'count{presscount_land}\tjudge{pressjudge_land}')
    #         if pressjudge_land == 1:
    #             print('land detected')
    #             break
    #
    #     print('finished')
    # except KeyboardInterrupt:
    #     print('interrupted')
    # except:
    #     print('finished')
