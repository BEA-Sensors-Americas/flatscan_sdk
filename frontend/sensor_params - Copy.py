import frontend.variable_enums as var


class SensorParams:

    def __init__(self):
        self.baud_rate = var.BAUD_RATE_921600
        self.com_port = var.COM_PORT_6
        self.transmission_mode = var.TRANSMISSION_MODE_SINGLE_SHOT
        self.angle_first = 0  # Minimum: 0
        self.angle_last = 108  # Maximum: 108
        self.detection_field_mode = var.DETECTION_FIELD_MODE_HS
        self.spots_number = 100
        self.optimization = var.OPTIMIZATION_NONE
        self.information_in_mdi = var.INFORMATION_IN_MID_DISTANCES_AND_REMISSIONS
        self.averaging = var.AVERAGING_NONE
        self.enable_can = True
        self.enable_ctn = True
        self.enable_facet = True

    def set_baud_rate(self, rate):
        # check rate?
        self.baud_rate = rate

    def set_com_port(self, port):
        self.com_port = port

    def set_transmission_mode(self, mode):
        self.transmission_mode = mode

    def set_optimization(self, op):
        self.optimization = op

    def set_information_in_mdi(self, info):
        self.information_in_mdi = info

    def set_averaging(self, ave):
        self.averaging = ave

    def set_detection_field_mode(self, detection_mode):
        self.detection_field_mode = detection_mode

    def set_enable_can(self, can):
        self.enable_can = can

    def set_enable_ctn(self, ctn):
        self.enable_ctn = ctn

    def set_enable_facet(self, facet):
        self.enable_facet = facet

    def set_spots_number(self, number):
        self.spots_number = number

    def set_angle_first(self, angle):
        self.angle_first = angle

    def set_angle_last(self, angle):
        self.angle_last = angle
