#モジュールのインポート
import datetime
import time
import gps_navigate
import gps
import calibration
import bmx055
import stuck2
import motor
import time
import other
import send
from collections import deque


#PID制御のテストコード

def get_theta_dest_gps(lon_dest, lat_dest, magx_off, magy_off):
    '''
    目標地点(dest)との相対角度を算出する関数
    ローバーが向いている角度を基準に、時計回りを正とする。

    theta_dest = 60 のとき、目標地点はローバーから見て右手60度の方向にある。

    -180 < theta_dest < 180

    Parameters
    ----------
    lon2 : float
        目標地点の経度
    lat2 : float
        目標地点の緯度
    magx_off : int
        地磁気x軸オフセット
    magy_off : int
        地磁気y軸オフセット

    '''
    #-----ローバーの角度を取得-----#
    magdata= bmx055.mag_dataRead()
    mag_x, mag_y = magdata[0], magdata[1]

    rover_angle = calibration.angle(mag_x, mag_y, magx_off, magy_off)
    direction = calibration.calculate_direction(lon_dest, lat_dest)
    azimuth = direction["azimuth1"]

    #-----目標地点との相対角度を算出-----#
    #ローバーが向いている角度を0度としたときの、目的地への相対角度。このとき時計回りを正とする。
    theta_dest = rover_angle - azimuth

    #-----相対角度の範囲を-180~180度にする-----#
    if theta_dest >= 180:
        theta_dest -= 360
    elif theta_dest <= -180:
        theta_dest += 360

    return theta_dest

def get_theta_dest(target_azimuth, magx_off, magy_off):
    '''
    #ローバーから目標地点までの方位角が既知の場合に目標地点(dest)との相対角度を算出する関数
    ローバーが向いている角度を基準に、時計回りを正とする。

    theta_dest = 60 のとき、目標地点はローバーから見て右手60度の方向にある。

    -180 < theta_dest < 180

    Parameters
    ----------
    lon2 : float
        目標地点の経度
    lat2 : float
        目標地点の緯度
    magx_off : int
        地磁気x軸オフセット
    magy_off : int
        地磁気y軸オフセット

    '''
    #-----ローバーの角度を取得-----#
    magdata= bmx055.mag_dataRead()
    mag_x, mag_y = magdata[0], magdata[1]

    rover_azimuth = calibration.angle(mag_x, mag_y, magx_off, magy_off)

    #-----目標地点との相対角度を算出-----#
    #ローバーが向いている角度を0度としたときの、目的地への相対角度。このとき時計回りを正とする。
    theta_dest = rover_azimuth - target_azimuth

    #-----相対角度の範囲を-180~180度にする-----#
    if theta_dest >= 180:
        theta_dest -= 360
    elif theta_dest <= -180:
        theta_dest += 360

    return theta_dest

theta_array = []
theta_differential_array = []

class PID_Controller:
    def __init__(self, kp, ki, kd, target, num_log, validate_ki):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target = target
        self.num_log = num_log
        self.validate_ki = validate_ki
        self.error = deque([0] * num_log, maxlen=num_log)
        self.integral = 0
        self.derivative = 0
        self.output = 0
        self.count = 0
    def get_output(self, measured, ):
        self.error.append(measured - self.target)
        self.integral += self.error[-1] 
        self.derivative = (self.error[-1] - self.error[-2]) 
        self.output = self.kp * self.error[-1] + self.ki * self.integral*(self.count >= self.validate_ki) + self.kd * self.derivative
        self.count += 1
        return self.output
    
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

def adjust_direction_PID(target_azimuth, magx_off, magy_off, theta_array: list):
    '''
    目標角度に合わせて方向調整を行う関数

    Parameters
    ----------
    target_theta : float
        ローバーを向かせたい方位角
    '''

    #パラメータの設定
    Kp = 0.4
    Kd_ = 3
    Ki_ = 0.03

    count = 0
    # controller = PID_Controller(kp=0.4, ki=0.03, kd=3, target=target_theta, num_log=5, validate_ki=25)
    
    print('adjust_direction_PID')

    #-----ローバーの角度の取得-----#
    error_theta = get_theta_dest(target_azimuth, magx_off, magy_off)

    # output = controller.get_output(theta)
    # print(controller.kp)
    
    print('error theta = ' + str(error_theta))

    theta_array.append(error_theta)

    #-----制御処理-----#
    #while abs(theta_array[-1]) > 5:
    while True:
        if count < 25:
            Ki = 0
            Kd = Kd_
        else:
            Ki = Ki_
            Kd = 5

        #-----角度の取得-----#
        error_theta = get_theta_dest(target_azimuth, magx_off, magy_off)

        #-----thetaの値を蓄積する-----#
        theta_array = latest_theta_array(error_theta, theta_array)

        #-----PID制御-----#
        #パラメータが0の場合それは含まれない
        m = PID_control(error_theta, theta_array, Kp, Ki, Kd)

        #-----モータの出力-----#

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
        rover_angle = calibration.angle(mag_x, mag_y, magx_off, magy_off)

        error_theta = get_theta_dest(target_azimuth, magx_off, magy_off)

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

def PID_drive(target_azimuth, magx_off, magy_off, theta_array: list, loop_num):
    '''
    目標地点までの方位角が既知の場合にPID制御により走行する関数
    '''
    #-----パラメータの設定-----#
    Kp = 0.4
    Kd_ = 3
    Ki_ = 0.03

    count = 0
    
    print('PID_drive')

    #-----相対角度の取得-----#
    error_theta = get_theta_dest(target_azimuth, magx_off, magy_off)

    theta_array.append(error_theta)

    #-----制御処理-----#
    #while abs(theta_array[-1]) > 5:
    for _ in range(loop_num):

        if count < 25:
            Ki = 0
            Kd = Kd_
        else:
            Ki = Ki_
            Kd = 5

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

        #直進補正分(m=0のとき直進するように設定するため)
        s = 30

        m = min(m, 15)
        m = max(m, -15)

        pwr_l = m + s
        pwr_r = -m + s

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

    #     check = 0
    #     bool_com = True
    #     for i in range(len(theta_array)):
    #         if abs(theta_array[i]) > 15:
    #             bool_com = False
    #             break
    #     if bool_com:
    #         break

    #     count += 1

    # motor.motor_stop(1)

def drive(lon_dest, lat_dest, thd_distance, t_run, log_path, t_start):
    '''
    任意の地点までPID制御により走行する関数
    
    Parameters
    ----------
    lon_dest : float
        目標地点の経度
    lat : float
        目標地点の緯度
    thed_distance : float
        目標地点に到達したと判定する距離（10mぐらいが望ましい？？短くしすぎるとうまく停止してくれない）
    t_adj_gps : float
        GPSの取得間隔
    log_path : 
        ログの保存先
    t_start : float
        開始時間
    '''

    #-----目標地点までの角度と距離を取得-----#
    direction = calibration.calculate_direction(lon_dest, lat_dest)
    distance = direction["distance"]

    while distance > thd_distance:
        #-----初期設定-----#
        stuck_count = 1

        #-----上向き判定-----#
        stuck2.ue_jug()

        #-----キャリブレーション-----#
        magx_off, magy_off = calibration.cal(30, -30, 40)

        #-----目標地点への角度を取得-----#
        direction = calibration.calculate_direction(lon_dest, lat_dest)
        target_azimuth = direction["azimuth1"]

        #-----PID制御による角度調整-----#
        adjust_direction_PID(target_azimuth, magx_off, magy_off, theta_array)

        #-----角度ログの出力-----#
        magdata = bmx055.mag_dataRead()
        mag_x = magdata[0]
        mag_y = magdata[1]

        log_rover_azimuth = calibration.angle(mag_x, mag_y, magx_off, magy_off)

        #-----GPS走行のための初期設定などもろもろ-----#
        t_cal = time.time() #キャリブレーションを行った時刻
        lat_old, lon_old = gps.location()

        other.log(log_path, datetime.datetime.now(), time.time() - t_start, lat_old, lon_old, log_rover_azimuth, direction['distance'])

        lat_str = "{:.6f}".format(lat_old)  # 緯度を小数点以下8桁に整形
        lon_str = "{:.6f}".format(lon_old)  # 経度を小数点以下8桁に整形
        send.send_data(lat_str)
        time.sleep(9)
        send.send_data(lon_str)
        time.sleep(9)

        while time.time() - t_cal <= t_run:
            print("-------gps走行-------")
            lat_now, lon_now = gps.location()
            print(lat_now, lon_now)

            #-----スタックチェック用の変数の更新-----#
            lat_new, lon_new = lat_now, lon_now
            direction = gps_navigate.vincenty_inverse(lat_now, lon_now, lat_dest, lon_dest)
            distance, azimuth = direction["distance"], direction["azimuth1"]

            #-----スタックチェック-----#
            if stuck_count % 25 == 0:
                if stuck2.stuck_jug(lat_old, lon_old, lat_new, lon_new, 1):
                    pass
                else:
                    stuck2.stuck_avoid()
                    pass
                lat_old, lon_old = gps.location()

            #
            if distance > thd_distance:
                for _ in range(25):
                    PID_drive(azimuth, magx_off, magy_off, theta_array, loop_num=25)
            else:
                break

            stuck_count += 1
            lat_new, lon_new = gps.location()
            print("whileの最下行")

        direction = calibration.calculate_direction(lon_dest, lat_dest)
        distance = direction["distance"]

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
    adjust_direction_PID(180, magx_off, magy_off, theta_array)

    time.sleep(1)

    adjust_direction_PID(0, magx_off, magy_off, theta_array)

    time.sleep(1)

    adjust_direction_PID(90, magx_off, magy_off, theta_array)

    time.sleep(1)

    adjust_direction_PID(270, magx_off, magy_off, theta_array)
    
    