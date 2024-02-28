import time
import utils.flatscan_occupancy as oc
import utils.flatscan_pattern_teachin as pattern
from api.flatscan_api import *
import math
import numpy as np


flatscan = Flatscan(8, baudrate=921600)
flatscan.set_can_and_frame_counter_field(1)

params = flatscan.get_parameters()
# get both distances and remission
flatscan.set_mdi_info(2)
# 333 is the number of spots but get 334 for testing
right_angel_point = (params["num_spots"] / (params['angle_last'] - params['angle_first']) * 100) * 90

teachIn = pattern.TeachInPattern(params["num_spots"], params['angle_first'], params['angle_last'], 100000, 100000)

for i in range(200):
    mdi = flatscan.get_mdi()
    teachIn.teach_in(mdi['distances'])
    teachIn.teach_in_remission(mdi['remissions'])

teachIn.finish_teach_in()
print("finished teach in")
print(teachIn.pattern)

while 1:
    mdi = flatscan.get_mdi()
    max_diff=teachIn.largest_diff_distance_index(mdi['distances'])
    print(max_diff)