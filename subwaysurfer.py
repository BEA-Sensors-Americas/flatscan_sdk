import time

from device_type.rad_distance_device import *
from device_type.controller import *
import pyautogui as pg
state=2
flatscan = Controller(4, 7)
while True:
    new_state = flatscan.update_occupancy()
    if new_state != state:
        state = new_state
        if state == 0:
            pg.press('up')
            # print("up")
        elif state == 1:
            pg.press('left')
            # print("left")
        elif state == 3:
            pg.press('down')
            # print("down")
        elif state == 2:
            pass
            # print("MIDE")
        elif state == 6:
            pg.press('space')
        elif state == 4:
            pg.press('right')
            # print("right")
