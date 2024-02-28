import math

from api.flatscan_api import *
from api.flatscan_parameters import *
import utils.flatscan_occupancy as utils
import numpy as np

LEFT_LIMIT = 450
FRONT_LIMIT = 260
ZONE_WIDTH = 1400
ZONE_LENDTH = 700
MIDDLE_LIMIT = 1100
UPPER_LIMIT = 1400

UP = 3
FRONT = 0
RESET = 6
LEFT = 1
RIGHT = 4
MIDDLE = 2
NO_ITEM = 5


class Controller:
    has_upper = False

    def __init__(self, port_number1, buffer_maximum_length=100, baudrate=BAUDRATE_DEFAULT):
        self.device = Flatscan(port_number1, baudrate=baudrate)

    def __init__(self, port_number1, port_number2, buffer_maximum_length=100, baudrate=BAUDRATE_DEFAULT):
        self.device = Flatscan(port_number1, baudrate=baudrate)
        if port_number2 >0:
            self.upper_device = Flatscan(port_number2, baudrate=baudrate)
            self.has_upper = True
        else :
            self.has_upper = False

    """Two sensors one zone on upper sensor, rectangular left, right, front zones on lower sensor
    return priority give to upper sensor"""

    def update_occupancy(self):
        mdi = self.device.get_mdi()

        distances = mdi['distances']
        # print(distances)
        # Extracting the points that are only in the rectangular zone from the whole data set
        right_angel_point = (len(distances) / (self.device.parameters_state['angle_last']
                                               - self.device.parameters_state['angle_first'])) * 9000

        rec_cor = utils.convert_distances_to_cartesian(distances, math.floor(right_angel_point))
        occupancy_left = utils.cartisian_get_in_rec(rec_cor, LEFT_LIMIT, ZONE_LENDTH)
        occupancy_middle = utils.cartisian_get_in_rec(rec_cor, MIDDLE_LIMIT, ZONE_LENDTH)
        occupancy_right = utils.cartisian_get_in_rec(rec_cor, ZONE_WIDTH, ZONE_LENDTH, depth_min=MIDDLE_LIMIT,
                                                     width_min=0)
        occupancy_front = utils.cartisian_get_in_rec(rec_cor, ZONE_WIDTH, FRONT_LIMIT)
        if not self.has_upper:
            upper_occupancy = True
        else:
            upper_distances = self.upper_device.get_mdi()
            upper_occupancy = utils.get_presence(upper_distances, UPPER_LIMIT)
        if not upper_occupancy:
            return UP
        elif occupancy_front:
            return FRONT
        elif occupancy_left and occupancy_right:
            return RESET
        elif occupancy_left:
            return LEFT
        elif occupancy_right:
            return RIGHT
        elif occupancy_middle:
            return MIDDLE
        else:
            return NO_ITEM

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
