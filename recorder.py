import time
import utils.flatscan_occupancy as oc
import utils.flatscan_pattern_teachin as pattern
from api.flatscan_api import *
import math
import numpy as np

flatscan = Flatscan(8, baudrate=921600)
flatscan.set_can_and_frame_counter_field(1)
# flatscan.set_heartbeat_period(5)
# flatscan.register_heartbeat_handler(lambda x: print("heartbeat: *", x[0], x[1]))
params = flatscan.get_parameters()
# get both distances and remission
flatscan.set_mdi_info(2)
# 333 is the number of spots but get 334 for testing
right_angel_point = (params["num_spots"] / (params['angle_last'] - params['angle_first']) * 100) * 90

teachIn = pattern.TeachInPattern(params["num_spots"], params['angle_first'], params['angle_last'], 100000, 100000)

for i in range(200):
    mdi = flatscan.get_mdi()
    teachIn.teach_in(mdi['distances'])
    teachIn.teach_in_remission(mdi['remission'])

teachIn.finish_teach_in()
print("finished teach in")
print(teachIn.pattern)

while 1:

    user_input = input("Enter a command to proceed on scanning").upper()
    diff = np.zeros(334)
    if user_input == "C":
        for i in range(50):
            mdi = flatscan.get_mdi()
            cur_diff = teachIn.compare_pattern(mdi['distances'])
            diff = np.add(diff, cur_diff)
    diff = diff / 50
    print(diff)
    res = np.any(diff[:-1] >= 20) or np.any(diff[1:] >= 20)
    print(res)
