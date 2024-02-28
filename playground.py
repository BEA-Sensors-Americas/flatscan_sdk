import numpy as np

from frontend import colors


def linear_scale(raw_data, target_value):
    scaled_data = (raw_data / 50.0) * target_value
    return scaled_data

# Example usage:
raw_data1 = 50
raw_data2 = 100
raw_data3 = 1

# Define the target value
target_value = 0.5

scaled_data1 = linear_scale(raw_data1, target_value)
scaled_data2 = linear_scale(raw_data2, target_value)
scaled_data3 = linear_scale(raw_data3, target_value)

print("Scaled Data 1:", scaled_data1)
print("Scaled Data 2:", scaled_data2)
print("Scaled Data 3:", scaled_data3)


def get_points_on_lines(distances, origin, angle_first, resolution, distance_map):
    x, y = origin
    distances = [0.5 * 0.1 * a for a in distances]

    size = int(max(distances) / resolution) + 1

    for d in distances:
        theta = np.linspace(0, np.pi / 2, int(d / resolution))
        points_x = np.round(x + np.cos(theta) * d / resolution).astype(int)
        points_y = np.round(y + np.sin(theta) * d / resolution).astype(int)

        distance_map[points_y, points_x] = colors.GRAY