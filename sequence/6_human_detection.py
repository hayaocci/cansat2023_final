import gps_navigate
import time 



if __name__ =="__main__":
    start_time = time.time()
    threshold = 20 * 60
    elapsed_time = time.time()-start_time
    if elapsed_time >= threshold:
        print("A")#終了へ行くように変更して
    else:
        print("B")#6回繰り返すところへ
        #
        