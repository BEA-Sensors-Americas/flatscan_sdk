import math
import numpy as np

START_INDEX = 0

def get_presence(mdi, limit):
    distance = mdi['distances']
    return any([d < limit for d in distance])



def get_presences_in_zones(mdi, limit, num_zones):
    distance = mdi['distances']
    num_spots = len(distance)
    spots_per_zone = math.floor(num_spots / num_zones)
    presences = []
    for i in range(num_zones):
        presences.append(any([d < limit for d in distance[i*spots_per_zone:(i+1)*spots_per_zone]]))
    return presences

def get_occupancy(mdi, limit, maxCount):
    distance = mdi['distances']
    prev = False
    prev_false_count = 0
    count = 0
    for d in distance:
        if prev and prev_false_count > 5:
            prev = False
            count = 0
            prev_false_count = 0
        if count > maxCount:
            return True
        if d < limit:
            count += 1
            prev = True
        else:
            if prev:
                prev_false_count += 1
    return False


def pol2cart(rho, phi):
    """
    :param rho: distance
    :param phi: angle in degree
    :return: rectangular coordinate for this spot
    """
    phi = phi / 360 * math.pi * 2
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return x, y


def cart2pol(x, y):
    """
    :param x: x coordinate
    :param y: y coordinate
    :return: angle(in rad) and distances
    """
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return rho, phi


def get_num_spots_in_rec(angle_first, angle_last, nums_spots):
    """
    :param angle_first:
    :param angle_last:
    :param nums_spots:
    :return: the number of spots in 90 degree rectangular area
    """
    return ((nums_spots / (angle_last - angle_first)) * 100) * 90


def clip_distances_in_rec(distances, nums_spots, depth, width, angle_first, angle_last):
    right_angle_point = math.floor(get_num_spots_in_rec(angle_first, angle_last, nums_spots))
    distances_in_rec = distances[START_INDEX:START_INDEX + right_angle_point]
    # TODO configuration might not start with 0
    padding = np.zeros(nums_spots - right_angle_point)
    result = np.array([get_data_point_in_rec_bond(dist, depth, width, i, right_angle_point) for i, dist in
                       enumerate(distances_in_rec)])
    res = np.append(result, padding)
    return res


def get_data_point_in_rec_bond(distance, depth, width, index, num_spots_in_rec):
    angle = index / num_spots_in_rec * 90
    coor = pol2cart(distance, angle)
    cart = [min(depth, coor[0]), min(width, coor[1])]
    pol = cart2pol(cart[0], cart[1])
    return pol[0]


def convert_distances_to_cartesian(distances, num_spots_in_rec):
    distances = distances[START_INDEX:START_INDEX + num_spots_in_rec]
    rec_cor = [pol2cart(dist, (i / num_spots_in_rec) * 90) for i, dist in enumerate(distances)]
    return rec_cor


def cartisian_get_in_rec(rec_cor, depth_max, width_max,depth_min=0, width_min=0, limit=5):
    in_rec = np.array([depth_max > x > depth_min and width_max > y > width_min for x, y in rec_cor])
    longest = np.diff(np.where(np.concatenate(([in_rec[0]], in_rec[:-1] != in_rec[1:], [True])))[0])[::2]
    longest = np.sort(longest)
    # print(longest)
    return len(longest) > 0 and longest[-1] > limit


def get_presence_in_rec(distances, depth, width, limit, num_spots_in_rec):
    # depth=x, width=y
    # TODO limit should be something you can configure, limit is the size of the detected object
    distances = distances[START_INDEX:START_INDEX + num_spots_in_rec]
    rec_cor = [pol2cart(dist, (i / num_spots_in_rec) * 90) for i, dist in enumerate(distances)]
    in_rec = np.array([x < depth and y < width for x, y in rec_cor])
    print(rec_cor)
    longest = np.diff(np.where(np.concatenate(([in_rec[0]], in_rec[:-1] != in_rec[1:], [True])))[0])[::2]
    longest = np.sort(longest)
    # print(longest)
    return len(longest) > 0 and longest[-1] > limit


def get_presence_in_rec2(distances, depth_max, width_max, depth_min, width_min, limit, num_spots_in_rec):
    # depth=x, width=y
    # TODO limit should be something you can configure, limit is the size of the detected object
    distances = distances[START_INDEX:START_INDEX + num_spots_in_rec]
    rec_cor = [pol2cart(dist, (i / num_spots_in_rec) * 90) for i, dist in enumerate(distances)]
    in_rec = np.array([x < depth_max and y < width_max and x > depth_min and y > width_min for x, y in rec_cor])
    # print(rec_cor)
    longest = np.diff(np.where(np.concatenate(([in_rec[0]], in_rec[:-1] != in_rec[1:], [True])))[0])[::2]
    longest = np.sort(longest)
    # print(longest)
    return len(longest) > 0 and longest[-1] > limit


def all_spots_in_rec(distances, depth, width, num_spots_in_rec, num_zones):
    distances = distances[START_INDEX:START_INDEX + num_spots_in_rec]
    rec_cor = [pol2cart(dist, (i / num_spots_in_rec) * 90) for i, dist in enumerate(distances)]
    print("rec_cor: ", rec_cor)
    each_zone_depth = depth / num_zones
    print("each zone depth: ", each_zone_depth)
    zones = []
    for i in range(num_zones):
        in_rec = np.array([(i * each_zone_depth) < x < ((i + 1) * each_zone_depth) and y < width for y, x in rec_cor])
        zones.append(np.sum(in_rec))
    return zones
