#gps running のdriveを一から作成

import datetime
import time
import gps_navigate
import gps
import bmx055
import motor #motor.move(l,r,t)
import im920sl
import calibration
import stuck2
import other

def angle_goal(magx_off, magy_off, lon2, lat2):
    """
    ゴールとの相対角度を算出する関数

    -180~180度
    """
    magdata = bmx055.mag_dataRead()
    mag_x = magdata[0]
    mag_y = magdata[1]
    theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
    direction = calibration.calculate_direction(lon2, lat2)
    azimuth = direction["azimuth1"]
    angle_relative = azimuth - theta
    if angle_relative >= 0:
        angle_relative = angle_relative if angle_relative <= 180 else angle_relative - 360
    else:
        angle_relative = angle_relative if angle_relative >= -180 else angle_relative + 360
    return angle_relative


def adjust_direction(theta, magx_off, magy_off, lon2, lat2):
#---------------方向調整---------------#

    theta = angle_goal(magx_off, magy_off, lon2, lat2)

    print('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')
    stuck2.ue_jug()
    
    base_pwr = 20
    pwr_1 = base_pwr + 20
    pwr_2 = base_pwr + 40

    an = base_pwr

    t_short = 0.1
    t_middle = 0.2
    t_long = 0.4

    count_adjust_direction = 1

    while 45 < theta <= 180 or -180 < theta < -45:
        print("adjust_direction" + str(count_adjust_direction))
        if 90 < theta <= 180 :
            motor.move(an, -an, t_long)
        elif -180 < theta < -90:
            motor.move(-an, an, t_long)
        elif 45 <= theta <= 90:
            motor.move(an, -an, t_middle)
        elif -90 <= theta <= -45:
            motor.move(-an, an, t_middle)
        elif 15 <= theta <= 45:
            motor.move(an, -an, t_short)
        elif -45 <= theta <= -15:
            motor.move(-an, an, t_short)
        
        theta = angle_goal(magx_off, magy_off, lon2, lat2)

        count_adjust_direction += 1

        if count_adjust_direction >= 5 and count_adjust_direction < 10:
            an = pwr_1
        elif count_adjust_direction >= 10:
            an = pwr_2

        #print('Calculated angle_relative: {theta}')
        print('-----調整後の相対角度-----')
        print(f'theta = {theta}')
        time.sleep(0.03)

    print("-----角度調整終了。お疲れ様でした。------")

    '''
    stuck_count = 1
    t_small = 0.1
    t_big = 0.2
    force = 40
    while 30 < theta <= 180 or -180 < theta < -30:
        if stuck_count >= 16:
            ##方向調整が不可能な場合はスタックしたとみなして、もう一度キャリブレーションからスタート##
            other.print_im920sl(
                "!!!!can't ajdust direction.   start stuck avoid!!!!!")
            stuck2.stuck_avoid()
            magx_off, magy_off = calibration.cal(40, 40, 30)
            stuck_count = -1
        if stuck_count % 7 == 0:
            other.print_im920sl('Increase output')
            force += 10
        if 30 <= theta <= 60:
            other.print_im920sl(
                f'theta = {theta}\t---rotation_ver1 (stuck:{stuck_count})')
            motor.move(force, -force, t_small)

        elif 60 < theta <= 180:
            other.print_im920sl(
                f'theta = {theta}\t---rotation_ver2 (stuck:{stuck_count})')
            motor.move(force, -force, t_big)

        elif -60 <= theta <= -30:
            other.print_im920sl(
                f'theta = {theta}\t---rotation_ver3 (stuck:{stuck_count})')
            motor.move(-force, force, t_small)
        elif -180 < theta < -60:
            other.print_im920sl(
                f'theta = {theta}\t---rotation_ver4 (stuck:{stuck_count})')
            motor.move(-force, force, t_big)
        else:
            print(f'theta = {theta}')

        stuck_count += 1
        stuck2.ue_jug()
        
    
        print('Calculated angle_relative: {theta}')
        time.sleep(1)
    other.print_im920sl(f'theta = {theta} \t rotation finished!!!')
    '''
def drive()


if __name__ == '__main__':
    # lat2 = 35.918548
    # lon2 = 139.908896
    # lat2 = 35.9234892
    # lon2 = 139.9118744
    #lat2 = 35.9240057
    #lon2 = 139.9114077
    #lat2 = 35.9184282 シダックス
    #lon2 = 139.9111039シダックス
    #lat2 = 35.9240087
    #lon2 = 139.9113212
    
    #生協入口
    #lat2 = 35.91818718
    #lon2 = 139.90814829

    #12号館前
    #lat2 = 35.91896917
    #lon2 = 139.90859362

    #グランドのゴール前
    #lat2 = 35.923914
    #lon2 = 139.912223

    #狭いグランドのほう
    #lat2 = 35.9243874
    #lon2 = 139.9114187

    #中庭の芝生
    #lat2 = 35.91817415
    #lon2 = 139.90825559

    lat2 = 35.9189778
    lon2 = 139.9071493 

    gps.open_gps()
    bmx055.bmx055_setup()
    motor.setup()

    drive(lon2, lat2, thd_distance=10, t_adj_gps=10)