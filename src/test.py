from time import sleep
import math

for i in range(0,10):
    sleep_time = math.ceil( 1 + 2 ** i / 2)
    print(sleep_time)
    #sleep(sleep_time)