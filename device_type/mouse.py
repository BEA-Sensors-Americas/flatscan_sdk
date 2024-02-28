import math

from api.flatscan_api import *
from api.flatscan_parameters import *
import utils.flatscan_occupancy as utils


class Mouse:
    def __init__(self, port_num):
        self.device = Flatscan(port_num, baudrate=BAUDRATE_DEFAULT)

    def click(self):
        print("Click")
