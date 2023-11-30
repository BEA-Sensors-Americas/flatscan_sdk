from api.flatscan_api import *


#A function that takes in a list of distances and returns a list of zones
#1 is something within the zone 0 is a cleared zone
def from_distances_to_detection(boundry_value, distances):
    """
    :param boundry_value: a boundry value to determine if a spot is occupied or not
    :param distances: list of distances
    :return: list of detection
    """
    detection = []
    for i in range(len(distances)):
        if distances[i] < boundry_value:
            pass
            #TODO: replace the line above and append 1 to detection
        else:
            pass
            #TODO: replace the line above and append 0 to detection
    return detection


#Step1: uncomment the line below and replace the # with the port number of your flatscan
flatscan=Flatscan(4)

#Step2: replace the 0 with the number of zones you want to use
num_zones=4

#Step3: uncomment the line below and replace the # with the boundry value you want to use
#boundry_value=500

#Step4: uncomment the line below and get the mdi
mdi=flatscan.get_mdi()
print(mdi)

#Step5: uncomment the line below and get the distances from mdi
#distances=

#Step6: uncomment the line below and print out distances and see how it looks like
#print("Distances:", distances)

#Step7: replace the [] below by calling the function from_distances_to_detection and print out the result
detection=[]

#Step8: get number of spots the sensor have and decide how many point you want to use for each zone
num_spots=0
spot_per_zone=0

zones=[]
for i in range(num_zones):
    zone_start=i*spot_per_zone
    zone_end=(i+1)*spot_per_zone
    is_there_any_detection= any(item > 0 for item in detection[zone_start:zone_end])
    zones.append(is_there_any_detection)

#print out zones see how it looks like


#Step9: repeat step 4 to step 8 in a for loop that run 1000 times
for i in range(1000):
    #TODO step 4 get mdi
    #TODO step 5 get distances
    #TODO step 7 get detection
    #TODO step 8 get zones
    print("zones: ", zones)
    time.sleep(0.1)














