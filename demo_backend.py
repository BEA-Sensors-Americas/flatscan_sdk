import time
import utils.flatscan_occupancy as oc
import utils.flatscan_pattern_teachin as pattern
from api.flatscan_api import *
import math

flatscan = Flatscan(4, baudrate=921600)
flatscan.set_can_and_frame_counter_field(1)
flatscan.set_heartbeat_period(5)
flatscan.register_heartbeat_handler(lambda x: print("heartbeat: *", x[0], x[1]))
params = flatscan.get_parameters()
right_angel_point = (params["num_spots"] / (params['angle_last'] - params['angle_first']) * 100) * 90
print(right_angel_point)
print(params["num_spots"])

teachIn = pattern.TeachInPattern(params["num_spots"], params['angle_first'], params['angle_last'], 705, 450)

for i in range(50):
    time.sleep(0.1)
    mdi = flatscan.get_mdi()
    teachIn.teach_in(mdi['distances'])

teachIn.finish_teach_in()

while (1):
    time.sleep(1)
    mdi = flatscan.get_mdi()
    teachIn.compare_pattern(mdi['distances'])

# while (1):
#    time.sleep(1)
#    mdi = flatscan.get_mdi()
#    #print(mdi['distances'][0: math.floor(right_angel_point)])
#    # print(oc.get_occupancy(mdi, 400, 20))
#    if(oc.get_presence_in_rec(mdi['distances'], 705, 450, 10, math.floor(right_angel_point))):
#        print("item detected!!!")

# print(flatscan.set_led("set", "red", "off", 5))
# flatscan.set_parameters(temperature=0, num_spots=200, mdi_info=0)
# print(flatscan.get_identity())
#
# k = 0
# while True:
#     time.sleep(3)
#     print(flatscan.get_mdi())
#     k += 1
#     if k == 2:
#         print("resetting heartbeat counter ...")
#         print(flatscan.reset_heartbeat_counter())
#     if k == 5:
#         print("resetting mdi counter ...")
#         print(flatscan.reset_mdi_counter())
