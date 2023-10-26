from api.flatscan_api import *
from api.flatscan_parameters import *
import numpy as np


class Controller:
    def __init__(self, port_number, buffer_maximum_length=100, baudrate=BAUDRATE_DEFAULT, yellow_dist=600,
                 red_dist=200):
        self.device = Flatscan(port_number, baudrate=baudrate)
        self.yellow_dist = yellow_dist
        self.red_dist = red_dist

    def get_device_type(self):
        return self.device_type


