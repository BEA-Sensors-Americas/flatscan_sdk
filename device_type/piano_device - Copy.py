import math

from api.flatscan_api import *
from api.flatscan_parameters import *
from utils.flatscan_occupancy import *
import numpy as np
class FlatScanPiano:
    def __init__(self, port_number, num_zones=6, buffer_maximum_length=100, baudrate=BAUDRATE_DEFAULT):
        self.device = Flatscan(port_number, baudrate=baudrate)
        self.num_zones = num_zones
        self.origin_point = [100,100]
        self.zone_width=50
        self.zone_depth=100
        self.zones=[]
        self.params = self.device.get_parameters()
        self.right_angel_point = int((self.params["num_spots"] / (self.params['angle_last'] - self.params['angle_first']) * 100) * 90)

    def print_mdi(self):
        mdi = self.device.get_mdi()
        zones=all_spots_in_rec(mdi['distances'],400,300,self.right_angel_point,14)
        print(zones)
        return zones