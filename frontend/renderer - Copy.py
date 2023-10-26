import threading

import numpy as np
from time import perf_counter
from PyQt6.QtCore import QThread
import math
from time import sleep
import frontend.colors as colors
from PyQt6.QtCore import QTimer
from frontend.api_calls import *
import utils.flatscan_occupancy as utils
from frontend.variable_enums import *


class Color_Palette:

    def __init__(self, background=colors.BLACK, origin=colors.YELLOW1, boundary=colors.GREEN, vertical=colors.RED1,
                 MDI=colors.VIOLET):
        self.set_colors(background, origin, boundary, vertical, MDI)

    def set_colors(self, background=colors.BLACK, origin=colors.YELLOW1, boundary=colors.GREEN, vertical=colors.RED1,
                   MDI=colors.VIOLET):
        self.background = background
        self.origin = origin
        self.boundary = boundary
        self.vertical = vertical
        self.MDI = MDI


class Renderer:

    def __init__(self, q_app, window, main_window, refresh_interval, h, w, af=0, al=108) -> None:
        self.window = window
        self.main_window = main_window
        self.main_window.resized.connect(self.resize_renderer)
        self.refresh_interval = refresh_interval
        self.max_x = self.window.plot_graph.size().width()
        self.max_y = self.window.plot_graph.size().height()
        self.angle_first = af
        self.angle_last = al
        self.color_palette = Color_Palette()
        self.base_frame = None
        self.next_frame_to_display = None
        self.origin_point = (self.max_x // 6, self.max_y // 6)
        self.origin_point_radius = 10
        self.draw_background_n_auxiliary_lines()
        # statistics
        self.start_ts = 0
        self.rendered_frames = 0
        # start updating frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.setInterval(refresh_interval)  # milliseconds 1000/fps
        self.timer.start()
        self.start_mdi_polling_thread(q_app)

    def start_reading_mdi(self):
        self.polling_thread.start_reading()

    def resize_renderer(self):
        self.max_x = self.window.plot_graph.size().width()
        self.max_y = self.window.plot_graph.size().height()
        self.origin_point = (self.max_x // 6, self.max_y // 8)
        self.origin_point_radius = 10
        self.draw_background_n_auxiliary_lines()

    def start_mdi_polling_thread(self, q_app):
        self.polling_thread = DataPollingThread()
        self.polling_thread.set_renderer(self)
        self.polling_thread.finished.connect(q_app.exit)
        self.polling_thread.start()

    def update_plot(self):
        if self.next_frame_to_display is None:
            return
        if self.start_ts == 0:
            self.start_ts = perf_counter()
        cur_data = self.next_frame_to_display
        self.window.plot_graph.setImage(cur_data)  # It takes numpy ndarray as argument
        # Calculate fps and show on UI.
        update_stop_ts = perf_counter()
        elapsed_time_seconds = update_stop_ts - self.start_ts
        frame_per_second = self.rendered_frames / elapsed_time_seconds
        self.window.label_fps.setText('FPS: ' + str(round(frame_per_second, 2)))

    # todo: better rescale strategy?
    def rescale_linear(self, array, new_min, new_max):
        newArray = [0.5 * self.clip(a, new_min, new_max) for a in array]
        minimum, maximum = np.min(array), np.max(array)
        m = (new_max - new_min) / (maximum - minimum)
        b = new_min - m * minimum
        # return m * array + b
        return newArray

    def clip(self, t, new_min, new_max):
        if (t > new_max):
            return 200 + 0.2 * t
        return 0.7 * t

    def render_w_new_mdi_data(self, measured_distances):
        measured_distances = self.rescale_linear(measured_distances, 180, 1400)
        angle_first = self.angle_first
        angle_last = self.angle_last
        num_points = len(measured_distances)
        new_frame = np.copy(self.base_frame)
        angle_delta = (angle_last - angle_first) / (num_points - 1)
        for i, dist in enumerate(measured_distances):
            point_position = self.translate_to_point_position(self.origin_point, dist, angle_delta, i)
            px, py = point_position
            px = round(px)
            py = round(py)
            radius = 2
            new_frame[px - radius:px + radius, py - radius:py + radius] = self.color_palette.MDI
        self.rendered_frames += 1
        self.next_frame_to_display = new_frame

    def translate_to_point_position(self, origin_point, dist, angle_delta, point_idx):
        angle = angle_delta * point_idx + self.angle_first
        x, y = origin_point
        if angle <= 20:
            angle = 20 - angle
            ang_rad = math.radians(angle)
            x_delta = math.sin(ang_rad) * dist
            new_y = y + math.cos(ang_rad) * dist
            new_x = x - x_delta
        else:
            angle = angle - 20
            ang_rad = math.radians(angle)
            x_delta = math.sin(ang_rad) * dist
            new_y = y + math.cos(ang_rad) * dist
            new_x = x + x_delta

        return (new_x, new_y)

    def set_new_frame_context(self, max_x=None, max_y=None, angle_first=-1, angle_last=-1, color_palette=None):
        changed = max_x or max_y or angle_first >= 0 or angle_last >= 0 or color_palette

        self.max_x = max_x if max_x else self.max_x
        self.max_y = max_y if max_y else self.max_y
        self.angle_first = angle_first if angle_first >= 0 else self.angle_first
        self.angle_last = angle_last if angle_last >= 0 else self.angle_last
        self.color_palette = color_palette if color_palette else self.color_palette
        self.start_ts = 0
        self.rendered_frames = 0
        if changed:
            self.draw_background_n_auxiliary_lines()

    def draw_background_n_auxiliary_lines(self):
        # empty canvas
        img = np.zeros((self.max_x, self.max_y, 3), dtype=(np.uint8))
        # paint background
        img[0:self.max_x, 0:self.max_y] = self.color_palette.background
        # draw origin point
        x, y = self.origin_point
        radius = self.origin_point_radius
        img[x - radius:x + radius, y - radius:y + radius] = self.color_palette.origin
        # draw boundary
        # print(img.shape, self.max_x, self.max_y)
        self.plot_boundary(img, self.max_x, self.max_y, self.origin_point, self.angle_first, self.angle_last)
        # draw vertical
        for i in range(self.max_y):
            img[x, i] = colors.RED1

        self.base_frame = img
        self.next_frame_to_display = img

    def calculate_point_relative_to_origin(self, max_x, max_y, origin_point, angle):
        x, y = origin_point
        if angle <= 20:
            angle = 20 - angle
            ang_rad = math.radians(angle)
            x_delta = math.tan(ang_rad) * (max_y - y)
            new_x = x - x_delta
            new_y = max_y
        else:
            angle = 110 - angle
            ang_rad = math.radians(angle)
            y_delta = math.tan(ang_rad) * (max_x - x)
            new_x = max_x
            new_y = y + y_delta
        return new_x, new_y

    def paint_line(self, max_x, max_y, img, line, color=np.array([0, 255, 0])):
        xx, yy, ww = line
        for i in range(len(yy)):
            x = xx[i]
            y = yy[i]
            w = ww[i]
            if x >= max_x or y >= max_y:
                break
            # print(y, x)
            img[x, y] = color * w

    def plot_boundary(self, img, max_x, max_y, origin_point, angle_first, angle_last):
        x, y = origin_point
        ep_x, ep_y = self.calculate_point_relative_to_origin(max_x, max_y, origin_point, angle_first)
        line = self.weighted_line(x, y, ep_x, ep_y, 4, 0, max_x - 1)
        self.paint_line(max_x, max_y, img, line)
        ep_x, ep_y = self.calculate_point_relative_to_origin(max_x, max_y, origin_point, angle_last)
        line = self.weighted_line(x, y, ep_x, ep_y, 4, 0, max_x - 1)
        self.paint_line(max_x, max_y, img, line)

    def trapez(self, y, y0, w):
        return np.clip(np.minimum(y + 1 + w / 2 - y0, -y + 1 + w / 2 + y0), 0, 1)

    def weighted_line(self, r0, c0, r1, c1, w, rmin=0, rmax=np.inf):
        if abs(c1 - c0) < abs(r1 - r0):
            xx, yy, val = self.weighted_line(c0, r0, c1, r1, w, rmin=rmin, rmax=rmax)
            return (yy, xx, val)

        if c0 > c1:
            return self.weighted_line(r1, c1, r0, c0, w, rmin=rmin, rmax=rmax)

        slope = (r1 - r0) / (c1 - c0)

        w *= np.sqrt(1 + np.abs(slope)) / 2

        x = np.arange(c0, c1 + 1, dtype=float)
        y = x * slope + (c1 * r0 - c0 * r1) / (c1 - c0)

        thickness = np.ceil(w / 2)
        yy = (np.floor(y).reshape(-1, 1) + np.arange(-thickness - 1, thickness + 2).reshape(1, -1))
        xx = np.repeat(x, yy.shape[1])
        vals = self.trapez(yy, y.reshape(-1, 1), w).flatten()

        yy = yy.flatten()

        mask = np.logical_and.reduce((yy >= rmin, yy < rmax, vals > 0))

        return (yy[mask].astype(int), xx[mask].astype(int), vals[mask])

    def update_occupancy(self, distances):
        right_angel_point = (len(distances) / (self.angle_last - self.angle_first)) * 90
        occupancy = utils.get_presence_in_rec(distances, 705, 410, 10, math.floor(right_angel_point))
        if occupancy:
            self.window.label_2.setText(str('Object Detected'))
        else:
            self.window.label_2.setText(str('Cleared'))


class DataPollingThread(QThread):

    def __init__(self, *args, **kwargs):
        QThread.__init__(self, *args, **kwargs)
        self.missedReading = 0
        self.STATE = RENDERER_NOT_CONNECTED
        self.state_semaphore = threading.Semaphore(1)

    def start_reading(self):
        self.STATE = RENDERER_START_READING
        self.state_semaphore.release()

    def run(self):
        while True:
            if self.STATE == RENDERER_NOT_CONNECTED:
                self.state_semaphore.acquire()
                continue
            elif self.STATE == RENDERER_START_READING:
                success = self.poll_mdi_from_sensor()
                if success == -1:
                    print("finished")
                    self.STATE = RENDERER_PAUSE
                sleep(0.1)
            else:
                #todo: disconnect comport
                self.state_semaphore.acquire()

    def set_renderer(self, renderer):
        self.renderer = renderer

    def poll_mdi_from_sensor(self):
        mdi = get_mdi()
        if mdi is None or 'distances' not in mdi:
            self.missedReading += 1
            if self.missedReading > ALLOWED_MISSED_MDI:
                return -1
            return 0
        distances = np.array(mdi['distances'])
        if not len(distances):
            return 0
            # distances = np.random.randint(200, 220, 108)

        self.renderer.render_w_new_mdi_data(distances)
        # for object detection
        self.renderer.update_occupancy(mdi['distances'])
        return 0
