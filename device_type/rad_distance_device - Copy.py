import math

from api.flatscan_api import *
from api.flatscan_parameters import *
import numpy as np


class RadDistance:
    def __init__(self, port_number, num_zones=6, buffer_maximum_length=100, baudrate=BAUDRATE_DEFAULT, yellow_dist=500,
                 red_dist=200):
        self.device = Flatscan(port_number, baudrate=baudrate)
        self.num_zones = num_zones
        # todo: add teachin pattern
        self.zones = np.zeros(num_zones)
        self.yellow_dist = yellow_dist
        self.red_dist = red_dist
        self.threshold = 3

    def get_object_in_zone(self, distances_in_zone):
        zone_red_info = np.array([True if dist < self.red_dist else False for dist in distances_in_zone])
        zone_yellow_info = np.array(
            [True if self.red_dist < dist < self.yellow_dist else False for dist in distances_in_zone])
        longest_red = np.sort(
            np.diff(np.where(np.concatenate(([zone_red_info[0]], zone_red_info[:-1] != zone_red_info[1:], [True])))[0])[
            ::2])
        longest_yellow = np.sort(np.diff(
            np.where(np.concatenate(([zone_yellow_info[0]], zone_yellow_info[:-1] != zone_yellow_info[1:], [True])))[
                0])[::2])
        if len(longest_red) > 0 and longest_red[-1] > self.threshold:
            return 2
        elif len(longest_yellow) > 0 and longest_yellow[-1] > self.threshold:
            return 1
        else:
            return 0

    def get_zone_info(self):
        num_spots = self.device.parameters_state['num_spots']
        spots_per_zone = math.floor(num_spots / self.num_zones)
        mdi = self.device.get_mdi()
        distances = mdi['distances']
        for i in range(self.num_zones):
            self.zones[i] = self.get_object_in_zone(np.array(distances[i * spots_per_zone:(i + 1) * spots_per_zone]))

    def detect_distance(self):
        for i in range(500):
            self.get_zone_info()
            print(self.zones)
            time.sleep(0.5)

    def detect_object(self):
        for i in range(500):
            self.get_zone_info()
            if 2 in self.zones:
                print("RED")
            elif 1 in self.zones:
                print("YELLOW")
            else:
                print("CLEAR")
            time.sleep(0.5)

    def change_zone_def(self, yellow, red):
        self.red_dist = red
        self.yellow_dist = yellow

    def change_num_of_zones(self, num_zones):
        self.num_zones = num_zones
        self.zones = np.zeros(num_zones)
