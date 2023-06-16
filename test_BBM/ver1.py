import time
import datetime
import sys


from other import print_xbee

import other


dateTime = datetime.datetime.now()

# variable for log
log_phase = other.filename('/home/pi/Desktop/cansat2021/log/phaseLog', 'txt')
log_release = other.filename(
    '/home/pi/Desktop/cansat2021/log/releaselog', 'txt')
log_landing = other.filename(
    '/home/pi/Desktop/cansat2021/log/landingLog', 'txt')
log_melting = other.filename(
    '/home/pi/Desktop/cansat2021/log/meltingLog', 'txt')
log_paraavoidance = other.filename(
    '/home/pi/Desktop/cansat2021/log/paraAvoidanceLog', 'txt')
log_panoramashooting = other.filename(
    '/home/pi/Desktop/cansat2021/log/panoramaLog', 'txt')
log_gpsrunning = other.filename(
    '/home/pi/Desktop/cansat2021/log/gpsrunningLog', 'txt')
log_photorunning = other.filename(
    '/home/pi/Desktop/cansat2021/log/photorunning', 'txt')
log_panoramacom = other.filename(
    '/home/pi/Desktop/cansat2021/log/panoramacomLog', 'txt')

def setup():
    global phase
    xbee.on()
    gps.open_gps()

def close():
    gps.close_gps()
    xbee.off()


if __name__ == '__main__':
    motor.setup()

    #######-----------------------Setup--------------------------------#######
    try:
        t_start = time.time()
        print_xbee('#####-----Setup Phase start-----#####')
        other.log(log_phase, "1", "Setup phase",
                  datetime.datetime.now(), time.time() - t_start)
        phase = other.phase(log_phase)
        if phase == 1:
            print_xbee(f'Phase:\t{phase}')
            setup()
            print_xbee('#####-----Setup Phase ended-----##### \n \n')
            print_xbee('####----wait----#### ')
            t_wait = 150
            for i in range(t_wait):
                print_xbee(t_wait-i)
                time.sleep(1)
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(setup)-----#####')
        print_xbee('#####-----Error(setup)-----#####\n \n')
    #######-----------------------------------------------------------########

    
    #######--------------------------gps--------------------------#######

    print_xbee('#####-----gps run start-----#####')
    other.log(log_phase, '7', 'GPSrun phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 7:
        gpsrunning.drive(lon2, lat2, th_distance, t_adj_gps, log_gpsrunning)
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print_xbee("message:{0}".format(e.with_traceback(tb)))
    #     print_xbee('#####-----Error(gpsrunning)-----#####')
    #     print_xbee('#####-----Error(gpsrunning)-----#####\n \n')

    