import time
import utils.flatscan_occupancy as oc
import utils.flatscan_pattern_teachin as pattern
from api.flatscan_api import *
import math

flatscan = Flatscan(7, baudrate=921600)
mdi=flatscan.get_mdi()
parameters=flatscan.get_parameters()
print(parameters)
num_spot=parameters['num_spots']
print(num_spot)
angular_resolution=(parameters['angle_last']-parameters['angle_first'])/num_spot
print(mdi)


for i in range(100000000):
    mdi=flatscan.get_mdi()
    print(mdi['distances'])
    time.sleep(0.1)



#while (1):
    #time.sleep(1)
    #mdi = flatscan.get_mdi()
    #teachIn.compare_pattern(mdi['distances'])

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
