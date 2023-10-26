import time

from device_type.rad_distance_device import *
import pyautogui as pg


flatscan = RadDistance(4, num_zones=3,yellow_dist=1000, red_dist=500);
while True:
    flatscan.get_zone_info()
    #print(flatscan.zones)
    if(2 in flatscan.zones):
        pg.press('down')
        print("down")
    elif(flatscan.zones[0]==1):
        pg.press('right')
        print("right")
    elif(flatscan.zones[2]==1):
        pg.press('left')
        print("left")
    elif(flatscan.zones[1]==0):
        pg.press('up')
        print("up")





