#モジュールのインポート
import calibration
import bmx055
import motor
import time

#PID制御のテストコード

theta_array = []
theta_differential_array = []

def make_theta_array(array: list, array_num: int):
    #-----決められた数の要素を含む空配列の作成-----#

    for i in range(array_num):
        array.append(0)
    
    return array

def latest_theta_array(theta, array:list):
    #-----thetaの値を蓄積する-----#

    #古い要素を消去
    del array[0]

    #新しい要素を追加
    array.append(theta)

    return array

def proportional_control(Kp, theta_array :list):
    #-----P制御-----#
    
    #-----最新のthetaの値を取得-----#
    theta_deviation = theta_array[-1]

    mp = Kp * theta_deviation

    return mp

def integral_control(Ki, theta_array: list):
    #I制御

    #積分係数の設定
    #Ki = 0.5

    #thetaの積分処理
    theta_integral = sum(theta_array)

    mi = Ki * theta_integral

    return mi

def differential_control(Kd, theta_array: list):
    #D制御

    #微分係数の設定
    #Kd = 0.5

    #thetaの微分処理
    for i in range(len(theta_array)):
        theta_differential_value = theta_array[i] - theta_array[i-1]
        theta_differential_array.append(theta_differential_value)

    #最新のthetaの微分値を取得
    theta_differential = theta_differential_array[-1]

    md = Kd * theta_differential

    return md

def PID_control(theta, theta_array: list, Kp=0.1, Ki=0.04, Kd=2.5):
    #-----PID制御-----#
    
    #-----初期設定-----# array_numは積分区間の設定
    #array = make_theta_array(array, array_num)

    #-----thetaの値を蓄積する-----#
    theta_array = latest_theta_array(theta, theta_array)

    #-----P制御-----#
    mp = proportional_control(Kp, theta_array)

    #-----I制御-----#
    mi = integral_control(Ki, theta_array)

    #-----D制御-----#
    md = differential_control(Kd, theta_array)

    #-----PID制御-----#
    m = mp + mi - md

    return m

def adjust_direction_north(target_theta, magx_off, magy_off, theta_array: list):

    #パラメータの設定
    Kp = 0.4
    Kd = 3
    Ki_ = 0.04

    count = 0
    
    print('adjust_direction_north')

    #-----角度の取得-----#
    magdata = bmx055.mag_dataRead()
    mag_x = magdata[0]
    mag_y = magdata[1]
    theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
    if theta > 180:
        theta = theta - 360

    error_theta = target_theta - theta
    if error_theta < -180:
        error_theta += 360
    elif error_theta > 180:
        error_theta -= 360
    
    print('theta = ' + str(error_theta))

    theta_array.append(error_theta)

    #-----制御処理-----#
    #while abs(theta_array[-1]) > 5:
    while True:

        if count < 25:
            Ki = 0
        else:
            Ki = Ki_

        #-----角度の取得-----#
        magdata = bmx055.mag_dataRead()
        mag_x = magdata[0]
        mag_y = magdata[1]
        theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)

        error_theta = target_theta - theta
        if error_theta < -180:
            error_theta += 360
        elif error_theta > 180:
            error_theta -= 360

        #-----thetaの値を蓄積する-----#
        theta_array = latest_theta_array(error_theta, theta_array)

        #-----PID制御-----#
        #パラメータが0の場合それは含まれない
        m = PID_control(error_theta, theta_array, Kp, Ki, Kd)

        #-----モータの出力-----#
        # if m >40:
        #     m = 40
        # elif m < -40:

        m = min(m, 40)
        m = max(m, -40)

        pwr_l = m
        pwr_r = -m

        print(f"{error_theta=}")
        print('left', pwr_l, 'right', pwr_r)

        #-----モータの操作-----#
        motor.motor_move(pwr_l, pwr_r, 0.01)
        #motor.move(pwr_l, pwr_r, 0.2)

        time.sleep(0.04)

        #-----角度の取得-----#
        magdata = bmx055.mag_dataRead()
        mag_x = magdata[0]
        mag_y = magdata[1]
        theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)

        error_theta = target_theta - theta

        if error_theta < -180:
            error_theta += 360
        elif error_theta > 180:
            error_theta -= 360

        check = 0
        bool_com = True
        for i in range(len(theta_array)):
            if abs(theta_array[i]) > 15:
                bool_com = False
                break
        if bool_com:
            break

        count += 1

    motor.motor_stop(1)

        


if __name__ == "__main__":

    #-----セットアップ-----#
    motor.setup()
    bmx055.bmx055_setup()

    #-----初期設定-----#
    theta_array = []
    theta_differential_array = []

    #-----要素数10の空配列の作成-----#
    theta_array = make_theta_array(theta_array, 5)

    #-----オフセットの取得-----#
    #-----キャリブレーション-----#
    print('Start Calibration')
    magx_off, magy_off = calibration.cal(30, -30, 40)

    #-----PID制御-----#
    adjust_direction_north(180, magx_off, magy_off, theta_array)

    time.sleep(1)

    adjust_direction_north(0, magx_off, magy_off, theta_array)

    time.sleep(1)

    adjust_direction_north(90, magx_off, magy_off, theta_array)

    time.sleep(1)

    adjust_direction_north(270, magx_off, magy_off, theta_array)