import frontend.variable_enums as var


def validate_detection_field(angle_first, angle_last, spots_number, detection_field_mode):
    # Check angles in field.
    if angle_first < 0 or angle_first > 108:
        print(var.MSG_INVALID_ANGLE_FIRST_INPUT)
        return False
    if angle_last < 0 or angle_last > 108:
        print(var.MSG_INVALID_ANGLE_LAST_INPUT)
        return False
    if angle_first >= angle_last:
        print(var.MSG_INVALID_ANGLE_FIRST_INPUT)
        return False

    # Check spots number according to detection field mode.
    if detection_field_mode == var.DETECTION_FIELD_MODE_HS:
        if spots_number < 1 or spots_number > 100:
            print(var.MSG_INVALID_SPOTS_NUMBER_IN_HS)
            return False

    if detection_field_mode == var.DETECTION_FIELD_MODE_HD:
        if spots_number < 4 or spots_number > 400 or spots_number % 4 != 0:
            print(var.MSG_INVALID_SPOTS_NUMBER_IN_HD)
            return False

    return True
