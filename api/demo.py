import time

from flatscan_api import *

flatscan = Flatscan(6, baudrate=921600)
flatscan.set_can_and_frame_counter_field(1)
flatscan.set_heartbeat_period(1)
flatscan.register_heartbeat_handler(lambda x: print(x[0], x[1], x[0] + x[1]))
time.sleep(5)
flatscan.register_heartbeat_handler(lambda x: print(x[0], x[1]))
while(1):
    time.sleep(1)
    print(flatscan.get_mdi())
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
