from api.flatscan_api import *

import numpy as np
import math
START_INDEX = 0
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


#a function that takes in distances, depth, width, limit, and num_spots_in_rec
# and return true if there is an object in the rectangular area
def get_presence_in_rec(distances, depth, width, num_spots_in_rec):
    # depth=x, width=y
    limit = 3
    distances = distances[START_INDEX:START_INDEX + num_spots_in_rec]
    rec_cor = [pol2cart(dist, (i / num_spots_in_rec) * 90) for i, dist in enumerate(distances)]
    in_rec = np.array([x < depth and y < width for x, y in rec_cor])
    longest = np.diff(np.where(np.concatenate(([in_rec[0]], in_rec[:-1] != in_rec[1:], [True])))[0])[::2]
    longest = np.sort(longest)
    return len(longest) > 0 and longest[-1] > limit



#Step1: uncomment the line below and replace the # with the port number of your flatscan
flatscan=Flatscan(4)

#Step2: replace the 0 with the depth and length you want to use
depth=400
width=400

#Step3: since we want a rectangular area as our zone starting with the angle 0, which means we only will take 90 degrees of the flatscan
#how many spot will be in this rectangular area? replace the 0 with the number of spots in this rectangular area
num_of_spots_total=400
angle_range=108
num_spots_in_rec=math.floor((num_of_spots_total/108)*90)

#Step4: uncomment the lines below and get the distance information mdi and the distances
mdi=flatscan.get_mdi()
print(mdi)

#Step5: replace [] with the distances you get from the mdi
distances=mdi['distances']

#print_out the distances and mdi
print("distances: ", distances)

#Step6: replace True in the line below by calling the function to get if there is an object in the rectangular area
presence=get_presence_in_rec(distances,depth, width, num_spots_in_rec)


#print out the presence
print("presence: ", presence)


#Step7: repeat step 4 to step 6 in a for loop that run 1000 times

for i in range(1000):
    mdi = flatscan.get_mdi()
    distances = mdi['distances']
    print("distances: ", distances)
    presence = get_presence_in_rec(distances, depth, width, num_spots_in_rec)
    print("presence: ", presence)
    time.sleep(0.1)

