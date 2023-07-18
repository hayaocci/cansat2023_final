import motor
import time

def e_power_test(t_move):
    print("-----Start e_power_test-----")
    s_time = time.time()
    while True:
        motor.move(40, 40, t_move)
        elapsed_time = time.time() - s_time
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
        time.sleep(10)
        
        if elapsed_time > 1200:
            break

    print("10mins run finish")

        


if __name__ == '__main__':
    motor.setup()
    #2分間走らせて、10秒休憩
    e_power_test(30)