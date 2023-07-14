#モータの出力を自動的に最適化する

import motor
import calibration

def motor_optimization(angle):
    #-----モータを最適化する-----#
    #-----引数は回転させたい角度-----#
    #各初期値を設定
    pwr = 35
    t_move = 0.1

    mag_angle = calibration.mag_angle()

    angle_dif = angle / mag_angle

    #-----モータを最適化する-----#
    while 0 <= angle_dif <= 5: