import numpy as np
import utils.flatscan_occupancy as oc

OBJECT_MISPLACEMENT_THRESHOLD = 50


class TeachInPattern:
    def __init__(self, num_spots, angle_first, angle_last, depth, width):
        self.num_spots = num_spots
        self.angle_first = angle_first
        self.angle_last = angle_last
        self.pattern = np.zeros(num_spots)
        self.remission_pattern = np.zeros(num_spots)
        self.num_samples = 0
        self.depth = depth
        self.width = width

    def teach_in(self, distances):
        if len(distances) != self.num_spots:
            # TODO: this might be caused by changed of setting or some other error during teach in
            return
        self.pattern = np.add(self.pattern, np.array(distances))
        self.num_samples += 1

    def teach_in_remission(self, remission):
        if len(remission) != self.num_spots:
            return
        self.remission_pattern = np.add(self.remission_pattern, np.array(remission))

    def clip_distances(self, distances):
        if len(distances) != self.num_spots:
            # TODO: this might be caused by changed of setting or some other error during teach in
            return
        return oc.clip_distances_in_rec(distances, self.num_spots, self.depth, self.width, self.angle_first,
                                        self.angle_last)

    def finish_teach_in(self):
        self.pattern = self.pattern / self.num_samples
        self.pattern = np.floor(self.pattern)
        self.pattern = self.clip_distances(self.pattern)

    def compare_pattern(self, distances):
        if len(distances) != self.num_spots:
            # TODO: this might be caused by changed of setting or some other error during teach in
            return
        # using mean square error to calculate differences
        distances = self.clip_distances(distances)
        mse = (np.square(self.pattern - np.array(distances))).mean(axis=None)
        return mse

    def object_misplacement(self, distances):
        mse = self.compare_pattern(distances)
        return mse >= OBJECT_MISPLACEMENT_THRESHOLD

    def largest_diff_distance_index(self, distances):
        distances = self.clip_distances(distances)
        absolute_difference = np.abs(distances - self.pattern)
        return np.argmax(absolute_difference)
