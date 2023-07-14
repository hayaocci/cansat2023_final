#モータの出力を自動的に最適化する

import motor
import calibration
import bmx055

def motor_optimization(angle):
    #-----モータを最適化する-----#
    #-----引数は回転させたい角度-----#
    #各初期値を設定
    pwr = 35
    t_move = 0.2

    magx_off, magy_off = calibration.cal(40, -40, 40)

    #ループに入れてあげるためにangle_difを設定している。
    angle_dif = 50

    #-----モータを最適化する-----#
    while 5 < angle_dif:
        #最適化を何回したか表示
        opt_count = 0
        print("最適化を" + str(opt_count) + "回行いました。")

        #回転前の角度を取得
        magx, magy, magz = bmx055.mag_dataRead()
        angle_bf = calibration.angle(magx, magy, magx_off, magy_off)
        
        #回転
        motor.move(pwr, -pwr, t_move)

        #回転後の角度を取得
        magx, magy, magz = bmx055.mag_dataRead()
        angle_af = calibration.angle(magx, magy, magx_off, magy_off)

        #回転した角度の計算
        rotated_angle = abs(angle_af - angle_bf)
        angle_dif = abs(angle - rotated_angle)
        angle_dif_ratio = angle_dif / angle
        print("理想の角度とのずれは" + str(angle_dif) + "度です。")

        #角度の最適化
        #cof_opt = 理論値 / 実測値
        cof_opt = angle / angle_dif

        if cof_opt < 1:
            pwr += 5
        elif cof_opt > 1:
            t_move = t_move * cof_opt
        






if __name__ == "__main__":
    a = int(input('回転させたい角度は？'))
    # pwr = int(input('モータの初期出力は？'))
    # t_move = float(input('モータの回転時間は？'))

    motor.setup()
    bmx055.bmx055_setup()
    magx_off, magy_off = calibration.cal(40, -40, 40)

    motor_optimization(a)