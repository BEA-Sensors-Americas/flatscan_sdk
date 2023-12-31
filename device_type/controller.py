import math

from api.flatscan_api import *
from api.flatscan_parameters import *
import utils.flatscan_occupancy as utils
import numpy as np


class Controller:
    def __init__(self, port_number1, buffer_maximum_length=100, baudrate=BAUDRATE_DEFAULT):
        self.device = Flatscan(port_number1, baudrate=baudrate)

    def __init__(self, port_number1, port_number2, buffer_maximum_length=100, baudrate=BAUDRATE_DEFAULT):
        self.device = Flatscan(port_number1, baudrate=baudrate)
        self.upper_device = Flatscan(port_number2, baudrate=baudrate)

    """Two sensors one zone on upper sensor, rectangular left, right, front zones on lower sensor
    return priority give to upper sensor"""

    def update_occupancy(self):
        mdi = self.device.get_mdi()

        distances = mdi['distances']
        # print(distances)
        right_angel_point = (len(distances) / (self.device.parameters_state['angle_last']
                                               - self.device.parameters_state['angle_first'])) * 9000

        rec_cor = utils.convert_distances_to_cartesian(distances, math.floor(right_angel_point))
        occupancy_left = utils.cartisian_get_in_rec(rec_cor, 450, 700)
        occupancy_middle = utils.cartisian_get_in_rec(rec_cor, 1100, 1000)
        occupancy_right = utils.cartisian_get_in_rec(rec_cor, 1400, 700, depth_min=1100, width_min=0)
        occupancy_front = utils.cartisian_get_in_rec(rec_cor, 1400, 260)

        upper_distances = self.upper_device.get_mdi()
        upper_occupancy = utils.get_presence(upper_distances, 1400)
        if not upper_occupancy:
            return 3
        elif occupancy_front:
            return 0
        elif occupancy_left and occupancy_right:
            return 6
        elif occupancy_left:
            return 1
        elif occupancy_right:
            return 4
        elif occupancy_middle:
            return 2
        else:
            return 5

    """Two sensors multiple zone on upper sensors, rectangular left, right, front zones on lower sensor
    no return priority all the same"""

    def update_occupancy_zones(self, num_zones):
        mdi = self.device.get_mdi()

        distances = mdi['distances']
        # print(distances)
        right_angel_point = (len(distances) / (self.device.parameters_state['angle_last']
                                               - self.device.parameters_state['angle_first'])) * 9000
        rec_cor = utils.convert_distances_to_cartesian(distances, math.floor(right_angel_point))
        occupancy_left = utils.cartisian_get_in_rec(rec_cor, 500, 1000)
        occupancy_middle = utils.cartisian_get_in_rec(rec_cor, 950, 1000)
        occupancy_right = utils.cartisian_get_in_rec(rec_cor, 1400, 1000, depth_min=950, width_min=0)
        occupancy_front = utils.cartisian_get_in_rec(rec_cor, 1400, 300)
        upper_distances = self.upper_device.get_mdi()
        upper_occupancy = utils.get_presences_in_zones(upper_distances, 1400, num_zones)
        return occupancy_left, occupancy_middle, occupancy_right, occupancy_front, upper_occupancy

    def get_device_type(self):
        return self.device_type
