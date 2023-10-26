TEMPERATURE_SETTING_MASK_W_NAME            = (1 << 1, "temperature setting")
MDI_INFO_SETTING_MASK_W_NAME               = (1 << 2, "MDI info setting")
DETECTION_FIELD_MODE_SETTING_MASK_W_NAME   = (1 << 3, "detection field mode setting")
SENSITIVITY_SETTING_MASK_W_NAME            = (1 << 4, "sensitivity setting")
NUM_SPOTS_SETTING_MASK_W_NAME              = (1 << 9, "number of spots setting")
ANGLE_FIRST_SETTING_MASK_W_NAME            = (1 << 12, "angle first setting")
ANGLE_LAST_SETTING_MASK_W_NAME             = (1 << 13, "angle last setting")
CAN_AND_FRAME_CTR_SETTING_MASK_W_NAME      = (1 << 14, "CAN and frame setting")
HEARTBEAT_PERIOD_SETTING_MASK_W_NAME       = (1 << 15, "heartbeat period setting")
FACET_NUMBER_FIELD_SETTING_MASK_W_NAME     = (1 << 16, "facet number field setting")
AVERAGING_SETTING_MASK_W_NAME              = (1 << 17, "averaging setting")

set_parameters_return_vals = [
    TEMPERATURE_SETTING_MASK_W_NAME,
    MDI_INFO_SETTING_MASK_W_NAME,
    DETECTION_FIELD_MODE_SETTING_MASK_W_NAME,
    SENSITIVITY_SETTING_MASK_W_NAME,
    NUM_SPOTS_SETTING_MASK_W_NAME,      
    ANGLE_FIRST_SETTING_MASK_W_NAME, 
    ANGLE_LAST_SETTING_MASK_W_NAME, 
    CAN_AND_FRAME_CTR_SETTING_MASK_W_NAME,
    HEARTBEAT_PERIOD_SETTING_MASK_W_NAME, 
    FACET_NUMBER_FIELD_SETTING_MASK_W_NAME, 
    AVERAGING_SETTING_MASK_W_NAME, 
]

def parse_set_parameters_return(r):
    r = int(r)
    msg = ""
    for mask, setting_name in set_parameters_return_vals:
        if r&mask:
            msg += setting_name
            msg += ', '
    if len(msg):
        msg = '[' + msg[:-2] + '] failed'
    if msg == "":
        return "Success"
    return msg

