"""
File Name: flatscan_utils.py
Description: FLATSCAN utils functions
© Carnegie Mellon University - MSE - Sensolution
"""
from api.flatscan_parameters import *
import serial

# Debug mode
DEBUG = False


def flatscan_sync_field_build(msg_len: int):
    """
    Build the SYNC field of the general communication frame

    :param msg_len: total length of the frame in bytes (length of SYNC + CMD + data + CHK)
    :return: the SYNC field in bytes
    """

    if DEBUG:
        print("flatscan_sync_field_build - MSG len:", msg_len)

    sync_msg_len = msg_len.to_bytes(SYNC_MSG_LEN_BYTES, 'little')
    sync_field = SYNC_PATTERN + SYNC_PROTOCOL + sync_msg_len + SYNC_VERIFICATION + SYNC_FUTURE

    if DEBUG:
        print("flatscan_sync_field_build - SYNC field:", sync_field.hex())

    return sync_field


def flatscan_chk_field_build(msg: bytes):
    """
    Build the CHK field of the general communication frame

    :param msg: all bytes of the SYNC, CMD and data fields
    :return: the CHK field in bytes
    """

    if DEBUG:
        print("flatscan_chk_field_build - MSG:", msg.hex())

    crc = 0
    for byte in msg:
        crc ^= byte << 8
        for i in range(8):
            crc = ((crc << 1) ^ (0x90d9 if crc & 0x8000 else 0)) & 0xFFFF
    crc = crc.to_bytes(2, 'little')

    if DEBUG:
        print("flatscan_chk_field_build - CHK:", crc.hex())

    return crc


def flatscan_message_validate(msg: bytes):
    """
    Validate the given message via SYNC field, CHK field,
    and the CMD field with its corresponding available message length

    :param msg: the message to be validated
    :return: true if the message is valid, false otherwise
    """

    if DEBUG:
        print("flatscan_message_validate - MSG:", msg.hex())

    msg_len = len(msg)
    if msg_len < MINIMAL_MSG_LEN:
        if DEBUG:
            print("flatscan_message_validate - message too short")
        return False

    sync_field = msg[: SYNC_FIELD_LEN]
    if sync_field != flatscan_sync_field_build(msg_len):
        return False
    chk_field = msg[-CHK_FIELD_LEN:]
    if chk_field != flatscan_chk_field_build(msg[: -CHK_FIELD_LEN]):
        return False
    cmd_field = msg[CMD_FIELD_OFFSET: CMD_FIELD_OFFSET + CMD_FIELD_LEN]
    if cmd_field not in MSG_VALID_CMD_SET and cmd_field not in ACK_CMD_SET:
        return False

    if cmd_field == MSG_HEARTBEAT_CMD:
        return msg_len in HEARTBEAT_MSG_LENS
    if cmd_field == MSG_SEND_PARAMETERS_CMD:
        return msg_len == PARAMETERS_MSG_LEN
    if cmd_field == MSG_SEND_IDENTITY_CMD:
        return msg_len == IDENTITY_MSG_LEN
    if cmd_field == MSG_EMERGENCY_CMD:
        return msg_len in EMERGENCY_MSG_LENS

    return True


def flatscan_parse_heartbeat_msg(msg: bytes):
    """
    Parse the HEARTBEAT message received from FLATSCAN

    :param msg: HEARTBEAT message in bytes
    :return: list of CAN number (BEA serial number) and heartbeat counter number,
    or an empty list if CAN and frame counter fields are disabled.
    """

    if DEBUG:
        print("flatscan_parse_heartbeat_msg - MSG:", msg.hex())

    data_field = msg[DATA_FIELD_OFFSET: -CHK_FIELD_LEN]
    if not data_field:
        print("CAN and frame counter fields are disabled")
        return []

    can_num = int.from_bytes(data_field[: HEARTBEAT_CAN_LEN], 'little')
    counter = int.from_bytes(data_field[-HEARTBEAT_CNTR_LEN:], 'little')
    return [can_num, counter]

    # Example HEARTBEAT messages
    # b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1c\x00\x46\x21'
    # b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1d\x00\x05\x8e'
    # b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1e\x00\x19\xef'
    # b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1f\x00\x5a\x40'


def flatscan_parse_parameters_msg(msg: bytes):
    """
    Parse the SEND_PARAMETERS message received from FLATSCAN

    :param msg: SEND_PARAMETERS message in bytes
    :return: dictionary that stores the received parameters configuration and verification bits
    """

    if DEBUG:
        print("flatscan_parse_parameters_msg - MSG:", msg.hex())

    data_field = msg[DATA_FIELD_OFFSET: -CHK_FIELD_LEN]
    res = dict()
    res['verification_bits'] = int.from_bytes(data_field[: PARAMETERS_VERIFICATION_BITS_LEN], 'little')
    res['temperature'] = data_field[PARAMETERS_TEMPERATURE_OFFSET]
    res['mdi_info'] = data_field[PARAMETERS_MDI_INFO_OFFSET]
    res['detection_field_mode'] = data_field[PARAMETERS_DETECTION_FIELD_MODE_OFFSET]
    res['sensitivity'] = data_field[PARAMETERS_SENSITIVITY_OFFSET]
    res['num_spots'] = int.from_bytes(
        data_field[PARAMETERS_NUM_SPOTS_OFFSET: PARAMETERS_NUM_SPOTS_OFFSET + PARAMETERS_NUM_SPOTS_LEN],
        'little')
    res['angle_first'] = int.from_bytes(
        data_field[PARAMETERS_ANGLE_FIRST_OFFSET: PARAMETERS_ANGLE_FIRST_OFFSET + PARAMETERS_ANGLE_FIRST_LEN],
        'little')
    res['angle_last'] = int.from_bytes(
        data_field[PARAMETERS_ANGLE_LAST_OFFSET: PARAMETERS_ANGLE_LAST_OFFSET + PARAMETERS_ANGLE_LAST_LEN],
        'little')
    res['can_and_frame_counter'] = data_field[PARAMETERS_CAN_AND_FRAME_COUNTER_OFFSET]
    res['heartbeat_period'] = data_field[PARAMETERS_HEARTBEAT_PERIOD_OFFSET]
    res['facet_number_field'] = data_field[PARAMETERS_FACET_NUMBER_FIELD_OFFSET]
    res['averaging'] = data_field[PARAMETERS_AVERAGING_OFFSET]
    return res


def flatscan_parse_identity_msg(msg: bytes):
    """
    Parse the SEND_IDENTITY message received from FLATSCAN

    :param msg: SEND_IDENTITY message in bytes
    :return: dictionary of FLATSCAN product part number (BEA TOF), software version, software revision,
    software prototype, CAN number of the detector (BEA serial number)
    """

    if DEBUG:
        print("flatscan_parse_identity_msg - MSG:", msg.hex())

    data_field = msg[DATA_FIELD_OFFSET: -CHK_FIELD_LEN]
    res = dict()
    res['product_part_number'] = int.from_bytes(data_field[: IDENTITY_PRODUCT_PART_NUMBER_LEN], 'little')
    res['software_version'] = data_field[IDENTITY_SOFTWARE_VERSION_OFFSET]
    res['software_revision'] = data_field[IDENTITY_SOFTWARE_REVISION_OFFSET]
    res['software_prototype'] = data_field[IDENTITY_SOFTWARE_PROTOTYPE_OFFSET]
    res['CAN_number'] = int.from_bytes(
        data_field[IDENTITY_CAN_NUMBER_OFFSET: IDENTITY_CAN_NUMBER_OFFSET + IDENTITY_CAN_NUMBER_LEN], 'little')
    return res


def flatscan_parse_emergency_msg(msg: bytes):
    """
    Parse the EMERGENCY message received from FLATSCAN

    :param msg: EMERGENCY message in bytes
    :return: dictionary of CAN number (BEA serial number) (if enabled), emergency counter (if enabled),
    RS485 module error code, and measuring head error code
    """

    # TODO:
    #  Add parameters_state param to check if the CAN and CNTR field is enabled
    #  Instead of using data field length to check
    #  Make it consistent with flatscan_parse_mdi_msg()
    #  as using the length of data field is impossible to identify which fields are enabled in mdi message

    if DEBUG:
        print("flatscan_parse_emergency_msg - MSG:", msg.hex())

    data_field = msg[DATA_FIELD_OFFSET: -CHK_FIELD_LEN]
    res = dict()
    if len(data_field) == EMERGENCY_DATA_WITH_CAN_CNTR_LEN:
        res['CAN_number'] = int.from_bytes(data_field[: EMERGENCY_CAN_LEN], 'little')
        res['emergency_counter'] = int.from_bytes(
            data_field[EMERGENCY_CNTR_OFFSET: EMERGENCY_CNTR_OFFSET + EMERGENCY_CNTR_LEN], 'little')
        res['RS485_error_code'] = data_field[EMERGENCY_RS485_OFFSET: EMERGENCY_RS485_OFFSET + EMERGENCY_RS485_LEN]
        res['measuring_head_error_code'] = data_field[EMERGENCY_MEASURING_HEAD_OFFSET:
                                                      EMERGENCY_MEASURING_HEAD_OFFSET + EMERGENCY_MEASURING_HEAD_LEN]
    else:
        res['RS485_error_code'] = data_field[: EMERGENCY_RS485_LEN]
        res['measuring_head_error_code'] = data_field[-EMERGENCY_MEASURING_HEAD_LEN:]
    return res


def flatscan_parse_mdi_msg(msg: bytes, parameters_state: dict):
    """
    Parse the MDI (measured distance information) message received from FLATSCAN

    :param msg: MDI message in bytes
    :param parameters_state: dictionary that stores the FLATSCAN parameters configuration
    :return: dictionary of CAN number, mdi frames counter, internal temperature, reference of the
    current mirror facet, measured distances, and measured remissions
    or None if the given parameters_state is invalid
    """

    if DEBUG:
        print("flatscan_parse_mdi_msg - MSG:", msg.hex())

    data_field = msg[DATA_FIELD_OFFSET: -CHK_FIELD_LEN]
    res = dict()
    offset = 0

    required_fields = ['can_and_frame_counter', 'temperature', 'facet_number_field', 'mdi_info', 'num_spots']
    for required_field in required_fields:
        if required_field not in parameters_state:
            print('Error: Given parameters_state is invalid, "%s" field is required' % required_field)
            return None

    if parameters_state['can_and_frame_counter'] == 1:
        res['CAN_number'] = int.from_bytes(data_field[offset: offset + MDI_CAN_LEN], 'little')
        offset += MDI_CAN_LEN
        res['mdi_frames_counter'] = int.from_bytes(data_field[offset: offset + MDI_CNTR_LEN], 'little')
        offset += MDI_CNTR_LEN
    if parameters_state['temperature'] == 1:
        res['temperature'] = int.from_bytes(data_field[offset: offset + MDI_CTN_LEN], 'little', signed=True)
        offset += MDI_CTN_LEN
    if parameters_state['facet_number_field'] == 1:
        res['facet'] = data_field[offset]
        offset += MDI_FACET_LEN
    if parameters_state['mdi_info'] != 1:
        res['distances'] = []
        for i in range(parameters_state['num_spots']):
            res['distances'].append(int.from_bytes(data_field[offset: offset + MDI_MEASUREMENT_LEN], 'little'))
            offset += MDI_MEASUREMENT_LEN
    if parameters_state['mdi_info'] != 0:
        res['remissions'] = []
        for i in range(parameters_state['num_spots']):
            res['remissions'].append(int.from_bytes(data_field[offset: offset + MDI_MEASUREMENT_LEN], 'little'))
            offset += MDI_MEASUREMENT_LEN
    return res


def flatscan_parameters_state_to_bytes(state: dict):
    return (b'\x00' + state['temperature'].to_bytes(1, 'little') + state['mdi_info'].to_bytes(1, 'little') +
            state['detection_field_mode'].to_bytes(1, 'little') + state['sensitivity'].to_bytes(1, 'little') +
            b'\x00' * 3 + state['num_spots'].to_bytes(2, 'little') + b'\x00' * 4 +
            state['angle_first'].to_bytes(2, 'little') + state['angle_last'].to_bytes(2, 'little') +
            state['can_and_frame_counter'].to_bytes(1, 'little') + state['heartbeat_period'].to_bytes(1, 'little') +
            state['facet_number_field'].to_bytes(1, 'little') + state['averaging'].to_bytes(1, 'little'))


def flatscan_serial_close(flatscan_serial):
    flatscan_serial.close()


def flatscan_serial_init(port_number: int, baudrate: int = BAUDRATE_DEFAULT):
    """
    Initialize the serial connection with FLATSCAN
    :param port_number: the COM port number connects with FLATSCAN
    :param baudrate: the baud rate of the serial communication
    :return: Serial connection object with FLATSCAN
    """

    try:
        flatscan_serial = serial.Serial("COM%s" % port_number, baudrate, timeout=FLATSCAN_TIMEOUT)
        print("FLATSCAN COM%d opened successfully" % port_number)
        return flatscan_serial
    except serial.SerialException:
        raise IOError('Failed to connect FLATSCAN via COM%s' % port_number)


def flatscan_rs485_error_parse(error_code):
    error_code = error_code[::-1]
    if error_code == b'\x50\x0a':
        return "Input supply low or high"
    elif error_code == b'\x50\x0d':
        return "Hardware failure in the RS485 module"
    elif b'\x80\x01' <= error_code <= b'\x80\xaa':
        return "Integrity test failure in RS485 module"
    elif error_code == b'\x00\x00':
        return "No error detected in the RS485 module"

    return "Unknown error code: " + error_code.hex()


def flatscan_measuring_head_error_parse(error_code):
    error_code = error_code[::-1]
    if error_code == b'\x81\x01' or error_code == b'\x81\x04':
        return "Communication error between head and RS485 module"
    elif b'\x50\x01' <= error_code <= b'\x50\x20':
        return "Hardware failure in the measuring head"
    elif b'\x80\x01' <= error_code <= b'\x80\xaa':
        return "Integrity test failure in the measuring head"
    elif error_code == b'\x00\x00':
        return "No error detected in the measuring head"

    return "Unknown error code: " + error_code.hex()
