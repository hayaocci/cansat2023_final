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

def PID_control(theta, theta_array: list, Kp=0.5, Ki=0.5, Kd=0.5):
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

def adjust_direction_north(magx_off, magy_off, theta_array: list):
    
    #パラメータの設定
    Kp = 0.15
    Kd = 0.3
    Ki = 0.01
    
    print('adjust_direction_north')

    #-----キャリブレーション-----#
    print('Start Calibration')
    magx_off, magy_off = calibration.cal(40, -40, 30)

    #-----角度の取得-----#
    magdata = bmx055.mag_dataRead()
    mag_x = magdata[0]
    mag_y = magdata[1]
    theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
    
    print('theta = ' + str(theta))

    theta_array.append(theta)

    #-----制御処理-----#
    while abs(theta_array[-1]) > 5:
        #-----角度の取得-----#
        magdata = bmx055.mag_dataRead()
        mag_x = magdata[0]
        mag_y = magdata[1]
        theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)

        #-----thetaの値を蓄積する-----#
        theta_array = latest_theta_array(theta, theta_array)

        #-----PID制御-----#
        #パラメータが0の場合それは含まれない
        m = PID_control(theta, theta_array, Kp, Ki, Kd)

        #-----モータの出力-----#
        pwr_l = -m
        pwr_r = m

        print('theta = ' + str(theta))
        print('left', pwr_l, 'right', pwr_r)

        #-----モータの操作-----#
        motor.move(pwr_l, pwr_r, 0.15)
        #motor.move(pwr_l, pwr_r, 0.2)

        time.sleep(0.1)

        #-----角度の取得-----#
        magdata = bmx055.mag_dataRead()
        mag_x = magdata[0]
        mag_y = magdata[1]
        theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)


if __name__ == "__main__":

    #-----セットアップ-----#
    motor.setup()
    bmx055.bmx055_setup()

    #-----初期設定-----#
    theta_array = []
    theta_differential_array = []

    #-----要素数10の空配列の作成-----#
    theta_array = make_theta_array(theta_array, 40)

    #-----オフセットの取得-----#
    magx_off, magy_off = 0, 0

    #-----PID制御-----#
    adjust_direction_north(magx_off, magy_off, theta_array)

    print('adjust complete')
    #-----直進-----#
    #motor.move(30, 30, 3)