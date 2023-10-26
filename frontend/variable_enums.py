BAUD_RATE_57600 = 57600  # 0
BAUD_RATE_115200 = 115200  # 1
BAUD_RATE_230400 = 230400  # 2
BAUD_RATE_460800 = 460800  # 3
BAUD_RATE_921600 = 921600  # 4

COM_PORT_1 = 1
COM_PORT_2 = 2
COM_PORT_3 = 3
COM_PORT_4 = 4
COM_PORT_5 = 5
COM_PORT_6 = 6

TRANSMISSION_MODE_SINGLE_SHOT = 0
TRANSMISSION_MODE_CONTINUOUS = 1

DETECTION_FIELD_MODE_HS = 0
DETECTION_FIELD_MODE_HD = 1

OPTIMIZATION_NONE = 0  # 0m
OPTIMIZATION_1 = 1  # 0-2.5m
OPTIMIZATION_2 = 2  # 0-3m
OPTIMIZATION_3 = 3  # 0-3.5m
OPTIMIZATION_4 = 4  # >3.5m

INFORMATION_IN_MID_DISTANCES = 0
INFORMATION_IN_MID_REMISSIONS = 1
INFORMATION_IN_MID_DISTANCES_AND_REMISSIONS = 2

AVERAGING_NONE = 0
AVERAGING_3_POINTS = 1
AVERAGING_3_POINTS_AND_TWO_NEIGHBORS = 2
AVERAGING_5_POINTS = 3
AVERAGING_5_POINTS_AND_TWO_NEIGHBORS = 4

MESSAGE = 'MESSAGE' #For debug
ERROR = 'ERROR'
INFO = 'INFO'
EMERGENCY = 'EMERGENCY'

MSG_INVALID_ANGLE_FIRST_INPUT = 'Invalid Angle First, Angle First should be a float with two decimal places and must ' \
                                'follow: 0.00 <= Angle First < Angle Last <= 108.00'
MSG_INVALID_ANGLE_LAST_INPUT = 'Invalid Angle Last, Angle Last should be a float with two decimal places and must ' \
                                'follow: 0.00 <=  Angle First < Angle Last <= 108.00'
MSG_INVALID_SPOTS_NUMBER_IN_HS = 'Invalid spots number in HS mode, number of spots should be between 1 and 100'
MSG_INVALID_SPOTS_NUMBER_IN_HD = 'Invalid spots number in HD mode, number of spots should be between 4 and 400, ' \
                                 'and must be a multiple of 4'
MSG_INVALID_DETECTION_FIELD_MODE = 'Invalid detection field mode selection. HD is not available under the current ' \
                                   'spots number setting'

SENSOR_NOT_CONNECTED = 'Sensor is not connected'

ALLOWED_MISSED_MDI = 3

RENDERER_NOT_CONNECTED =1
RENDERER_START_READING =2
RENDERER_PAUSE =3