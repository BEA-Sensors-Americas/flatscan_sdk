import time

from device_type.rad_distance_device import *
from device_type.controller import *
import pyautogui as pg

flatscan = Controller(4)
prev_left = False
prev_middle = False
prev_right = False
prev_front = False

while True:
    new_state = flatscan.update_occupancy_zones(3)

    left = new_state[0]
    middle = new_state[1]
    right = new_state[2]
    front = new_state[3]
    upper = new_state[4]
    print(upper)
    if (not prev_left) and left:
        pg.keyDown('left')
    elif prev_left and (not left):
        pg.keyUp('left')
    if (not prev_front) and front:
        print('UP')
        pg.press('up')
    if (not prev_right) and right:
        pg.keyDown('right')
    elif prev_right and (not right):
        pg.keyUp('right')
    prev_left = left
    prev_middle = middle
    prev_right = right
    prev_front = front
