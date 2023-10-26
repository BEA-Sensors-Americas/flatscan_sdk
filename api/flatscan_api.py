"""
File Name: flatscan_api.py
Description: FLATSCAN APIs
API Doc: https://docs.google.com/document/d/1uuOCYMFOmZa1XBUKZJg2UgN4WTvTgFU5yzM-E3mtnvA/edit?usp=sharing
© Carnegie Mellon University - MSE - Sensolution
"""
import json
import threading

import time
from datetime import datetime

from collections import deque

import api.flatscan_utils as utils
from api.flatscan_parameters import *
import serial

# Debug mode
DEBUG = True


class FlatscanReadThread(threading.Thread):
    def __init__(self, flatscan_serial, conditions, buffers, buffer_maximum_length, heartbeat_handler=None,
                 emergency_hander=None):
        super().__init__()
        self.flatscan_serial = flatscan_serial
        self.stopEvent = threading.Event()
        self.conditions = conditions
        self.buffers = buffers
        self.buffer_maximum_length = buffer_maximum_length
        self.heartbeat_handler = heartbeat_handler
        self.emergency_handler = emergency_hander
        self.debug_log = {}
        self.emergency_handler = None
        self.heartbeat_handler = None

    def log_event(self, action):
        timestamp = datetime.now()
        self.debug_log[timestamp.strftime("%Y-%m-%d %H:%M:%S")] = action

    def export_log(self, file_path):
        try:
            file = open(file_path, 'w')
            file.write(json.dumps(self.debug_log))
            file.close()
        except OSError:
            return False
        return True

    def run(self):
        self.read_message()

    def stop(self):
        self.stopEvent.set()

    def register_heartbeat_handler(self, heartbeat_handler):
        self.heartbeat_handler = heartbeat_handler

    def register_emergency_handler(self, emergency_handler):
        self.emergency_handler = emergency_handler

    def read_message(self):
        """
        Continuously read message from FLATSCAN serial
        """

        # State:
        # 1. Find SYNC Pattern 0xbea01234
        # 2. Read next 7 bytes for SYNC field and parse total size of the frame
        # 3. Read CMD, data and CHK fields
        # 4. Validate and distribute received message based on CMD field

        while not self.stopEvent.isSet():
            # State 1
            while not self.stopEvent.isSet():
                self.log_event("serial port closed")
                try:
                    sync_pattern = self.flatscan_serial.read(4)
                    #print(sync_pattern)
                    if sync_pattern == SYNC_PATTERN:
                        #print("ASDADS")
                        break
                except serial.serialutil.SerialException or TypeError:
                    self.log_event("serial port closed")
                    print("serial port closed")
                    return

            # State 2
            sync_field = sync_pattern + self.flatscan_serial.read(SYNC_FIELD_LEN - SYNC_PATTERN_LEN)
            msg_len = int.from_bytes(sync_field[SYNC_MSG_LEN_OFFSET: SYNC_MSG_LEN_OFFSET + SYNC_MSG_LEN_BYTES],
                                     'little')

            # State 3
            msg = sync_field + self.flatscan_serial.read(msg_len - SYNC_FIELD_LEN)

            # State 4
            if not utils.flatscan_message_validate(msg):
                self.log_event("Invalid message received, skipped")
                print("Invalid message received, skipped")
                print(msg.hex())
                continue
            cmd_field = msg[CMD_FIELD_OFFSET: CMD_FIELD_OFFSET + CMD_FIELD_LEN]
            self.conditions[cmd_field].acquire()
            # print(cmd_field)
            try:
                if cmd_field in MSG_VALID_CMD_SET:
                    self.buffers[cmd_field].append(msg)
                    if len(self.buffers[cmd_field]) > self.buffer_maximum_length:
                        self.buffers[cmd_field].popleft()
                if cmd_field in {MSG_SEND_PARAMETERS_CMD, MSG_SEND_IDENTITY_CMD, MSG_MDI_CMD}.union(ACK_CMD_SET):
                    self.conditions[cmd_field].notify()
                if cmd_field == MSG_EMERGENCY_CMD and self.emergency_handler is not None:
                    self.log_event("Emergency received")
                    self.emergency_handler(utils.flatscan_parse_emergency_msg(msg))
                if cmd_field == MSG_HEARTBEAT_CMD and self.heartbeat_handler is not None:
                    self.log_event("HEARTBEAT received")
                    self.heartbeat_handler(utils.flatscan_parse_heartbeat_msg(msg))
            finally:
                self.conditions[cmd_field].release()
        print("event received")


def enable_logging():
    global DEBUG
    DEBUG = True


class Flatscan:
    def __init__(self, port_number, buffer_maximum_length=100, baudrate=BAUDRATE_DEFAULT):
        self.flatscan_serial = utils.flatscan_serial_init(port_number, baudrate)

        self.buffers = {cmd: deque() for cmd in MSG_VALID_CMD_SET}
        self.conditions = {cmd: threading.Condition() for cmd in MSG_VALID_CMD_SET.union(ACK_CMD_SET)}
        self.read_thread = FlatscanReadThread(self.flatscan_serial, self.conditions, self.buffers,
                                              buffer_maximum_length)
        self.read_thread.start()
        self.debug_log = {}

        self.parameters_state = self.get_parameters()
        if self.parameters_state is None:
            utils.flatscan_serial_close(self.flatscan_serial)
            raise ValueError('Connection Timeout: please check if the com port and baudrate you selected')
        self.get_mdi()

    def handle_timeout(self, msg):
        print(msg)


    def export_log(self, file_path):
        self.read_thread.export_log(file_path)
        try:
            file = open(file_path, 'w')
            file.write(json.dumps(self.debug_log))
            file.close()
        except OSError:
            return False
        return True

    def log_action(self, action, value):
        timestamp = datetime.now()
        self.debug_log[action + " " + timestamp.strftime("%Y-%m-%d %H:%M:%S")] = str(value)

    def enable_log(self):
        DEBUG = True

    def set_baudrate(self, baudrate: int):
        """
        Set baudrate for FLATSCAN serial communication. The new value is automatically saved in EEPROM and the baud rate
        is modified at the next power on

        :param baudrate: baud rate of the serial communication. Take into account the quantity of data and the period of
            the transmission in HS and HD modes. If the baud rate is not sufficient, measurement information will be
            lost. Available value: 57600, 115200, 230400, 460800, 921600.
        :return: boolean ACK
        """

        if baudrate not in BAUDRATE_AVAILABLE:
            return False

        if DEBUG:
            self.log_action("set baudrate", baudrate)

        sync_field = utils.flatscan_sync_field_build(SET_BAUDRATE_LEN)
        data_field = BAUDRATE_AVAILABLE.index(baudrate).to_bytes(1, 'little')
        crc_field = utils.flatscan_chk_field_build(sync_field + SET_BAUDRATE_CMD + data_field)
        self.flatscan_serial.write(sync_field + SET_BAUDRATE_CMD + data_field + crc_field)
        return self.__get_ack(ACK_SET_BAUDRATE)

    def set_parameters(self, temperature: int = None, mdi_info: int = None, detection_field_mode: int = None,
                       sensitivity: int = None, num_spots: int = None, angle_first: int = None, angle_last: int = None,
                       can_and_frame_counter: int = None, heartbeat_period: int = None, facet_number_field: int = None,
                       averaging: int = None):
        """
        Set FLATSCAN parameters

        :param temperature: CTN (temperature) field in measurement frames (0: disable, 1: enable)
        :param mdi_info: information in MDI (0: send distances only, 1: send remissions only, 2: send both)
        :param detection_field_mode: 0: HS-high speed, 1: HD-high density
        :param sensitivity: sensitivity and immunity optimization with respect to the size of the detection field
            (maximum distance)
            - 0: no optimization (maximum sensitivity)
            - 1: range = 0 to 2.5m (minimum sensitivity)
            - 2: range = 0 to 3m
            - 3: range = 0 to 3.5m
            - 4: range longer than 3.5m (maximum sensitivity)
        :param num_spots: number of spots in the field (take into account restrictions linked to HS and HD modes)
        :param angle_first: limit of the detection field (unit: 0.01 degree)
        :param angle_last: limit of the detection field (unit: 0.01 degree)
        :param can_and_frame_counter: CAN and frame counter fields in measurement, heartbeat, emergency frames
            (0: disable, 1: enable)
        :param heartbeat_period: range 0 to 255. If value is 0, heartbeat is disabled (unit: 1 sec)
        :param facet_number_field: facet number field in MDI (0: disable, 1: enable)
        :param averaging: averaging setting)
            - 0: no averaging
            - 1: averaging 3 points in time
            - 2: averaging 3 points in time + 2 neighbors
            - 3: averaging 5 points in time
            - 4: averaging 5 points in time + 2 neighbors
        :return: verification bits that confirms if the value configured by the controller is correct.
            Verification bits set to 1 means that the associated parameter value is not valid.
            - Bit 1: temperature
            - Bit 2: mdi_info
            - Bit 3: detection_field_mode
            - Bit 4: sensitivity
            - Bit 9: num_spots
            - Bit 12: angle_first
            - Bit 13: angle_last
            - Bit 14: can_and_frame_counter
            - Bit 15: heartbeat_period
            - Bit 16: facet_number_field
            - Bit 17: averaging
        """

        sync_field = utils.flatscan_sync_field_build(SET_PARAMETERS_LEN)
        if temperature is not None:
            self.parameters_state['temperature'] = temperature
        if mdi_info is not None:
            self.parameters_state['mdi_info'] = mdi_info
        if detection_field_mode is not None:
            self.parameters_state['detection_field_mode'] = detection_field_mode
        if sensitivity is not None:
            self.parameters_state['sensitivity'] = sensitivity
        if num_spots is not None:
            self.parameters_state['num_spots'] = num_spots
        if angle_first is not None:
            self.parameters_state['angle_first'] = angle_first
        if angle_last is not None:
            self.parameters_state['angle_last'] = angle_last
        if can_and_frame_counter is not None:
            self.parameters_state['can_and_frame_counter'] = can_and_frame_counter
        if heartbeat_period is not None:
            self.parameters_state['heartbeat_period'] = heartbeat_period
        if facet_number_field is not None:
            self.parameters_state['facet_number_field'] = facet_number_field
        if averaging is not None:
            self.parameters_state['averaging'] = averaging
        if DEBUG:
            self.log_action("parameter set to", self.parameters_state)

        print(self.parameters_state)

        data_field = utils.flatscan_parameters_state_to_bytes(self.parameters_state)
        crc_field = utils.flatscan_chk_field_build(sync_field + SET_PARAMETERS_CMD + data_field)
        self.flatscan_serial.write(sync_field + SET_PARAMETERS_CMD + data_field + crc_field)

        msg = self.__get_msg(MSG_SEND_PARAMETERS_CMD)
        if msg == None:
            self.handle_timeout("time out from set params")
        self.parameters_state = utils.flatscan_parse_parameters_msg(msg)
        if DEBUG:
            self.log_action("parameter return", self.parameters_state)
            print(self.parameters_state)
        return self.parameters_state['verification_bits']

    def set_temperature_field(self, temperature: int):
        """
        Set whether enable CTN (temperature) field in measurement frames

        :param temperature: 0: disable, 1: enable
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(temperature=temperature)
        return (verification_bits >> VERIFICATION_BIT_TEMPERATURE) & 1 != 1

    def set_mdi_info(self, mdi_info: int):
        """
        Set information in MDI

        :param mdi_info: 0: send distances only, 1: send remissions only, 2: send both
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(mdi_info=mdi_info)
        return (verification_bits >> VERIFICATION_BIT_MDI_INFO) & 1 != 1

    def set_detection_field_mode(self, detection_field_mode: int):
        """
        Set detection field mode to high speed or high density

        :param detection_field_mode: 0: HS-high speed, 1: HD-high density
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(detection_field_mode=detection_field_mode)
        return (verification_bits >> VERIFICATION_BIT_DETECTION_FIELD_MODE) & 1 != 1

    def set_sensitivity_and_optimization(self, sensitivity_optimization: int):
        """
        Set sensitivity and immunity optimization with respect to the size of the detection field (maximum distance)

        :param sensitivity_optimization:
            - 0: no optimization (maximum sensitivity)
            - 1: range = 0 to 2.5m (minimum sensitivity)
            - 2: range = 0 to 3m
            - 3: range = 0 to 3.5m
            - 4: range longer than 3.5m (maximum sensitivity)
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(sensitivity=sensitivity_optimization)
        return (verification_bits >> VERIFICATION_BIT_SENSITIVITY) & 1 != 1

    def set_num_spots(self, num_spots: int):
        """
        Set number of spots in the field (take into account restrictions linked to HS and HD modes)

        :param num_spots: number of spots
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(num_spots=num_spots)
        return (verification_bits >> VERIFICATION_BIT_NUM_SPOTS) & 1 != 1

    def set_angle_first(self, angle_first: int):
        """
        Set limit of the detection field (unit: 0.01 degree)

        :param angle_first: limit of the detection field
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(angle_first=angle_first)
        return (verification_bits >> VERIFICATION_BIT_ANGLE_FIRST) & 1 != 1

    def set_angle_last(self, angle_last: int):
        """
        Set limit of the detection field (unit: 0.01 degree)

        :param angle_last: limit of the detection field
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(angle_last=angle_last)
        return (verification_bits >> VERIFICATION_BIT_ANGLE_LAST) & 1 != 1

    def set_can_and_frame_counter_field(self, can_and_frame_counter: int):
        """
        Set whether enable CAN and frame counter fields in measurement, heartbeat, emergency frames

        :param can_and_frame_counter: 0: disable, 1: enable
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(can_and_frame_counter=can_and_frame_counter)
        return (verification_bits >> VERIFICATION_BIT_CAN_AND_FRAME_COUNTER) & 1 != 1

    def set_heartbeat_period(self, heartbeat_period: int):
        """
        Set heartbeat period

        :param heartbeat_period: range 0 to 255. If value is 0, heartbeat is disabled (unit: 1 sec)
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(heartbeat_period=heartbeat_period)
        return (verification_bits >> VERIFICATION_BIT_HEARTBEAT_PERIOD) & 1 != 1

    def set_facet_number_field(self, facet_number_field: int):
        """
        Set whether enable facet number field in MDI

        :param facet_number_field: 0: disable, 1: enable
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(facet_number_field=facet_number_field)
        return (verification_bits >> VERIFICATION_BIT_FACET_NUMBER_FIELD) & 1 != 1

    def set_averaging_setting(self, averaging_setting: int):
        """
        Set averaging setting

        :param averaging_setting:
            - 0: no averaging
            - 1: averaging 3 points in time
            - 2: averaging 3 points in time + 2 neighbors
            - 3: averaging 5 points in time
            - 4: averaging 5 points in time + 2 neighbors
        :return: True if successfully set, False otherwise
        """
        verification_bits = self.set_parameters(averaging=averaging_setting)
        return (verification_bits >> VERIFICATION_BIT_AVERAGING) & 1 != 1

    def set_led(self, action: str, color: str, blink_color: str, blink_freq: int):
        """
        Set LED light on FLATSCAN

        :param action: action of the LED light ["set" or "blink"]
        :param color: color of the LED light ["off", "red", "orange", "green"]
        :param blink_color: blink color of the LED light (ignored if action is "set")
        :param blink_freq: blink frequency in Hz (ignored if action is "set") [1-10]
        :return: boolean ACK
        """

        if (action not in LED_ACTIONS or color not in LED_COLORS or
                blink_color not in LED_COLORS or blink_freq not in LED_FREQ_RANGE):
            if DEBUG:
                self.log_action("invalid argument for set led", 0)
            raise ValueError(
                'Invalid arguments provided for flatscan_set_led, please refer the API guide and try again.')

        sync_field = utils.flatscan_sync_field_build(SET_LED_LEN)
        data_field = (LED_ACTIONS[action] + LED_COLORS[color] + LED_COLORS[blink_color] +
                      blink_freq.to_bytes(1, 'little'))
        crc_field = utils.flatscan_chk_field_build(sync_field + SET_LED_CMD + data_field)
        self.flatscan_serial.write(sync_field + SET_LED_CMD + data_field + crc_field)

        return self.__get_ack(ACK_SET_LED)

    def get_emergency(self):
        """
        Get FLATSCAN emergency

        :return: dictionary that stores the CAN number, emergency counter,
            RS485 module error code and measuring head error code
        """
        if DEBUG:
            self.log_action("get emergency called", 0)
        sync_field = utils.flatscan_sync_field_build(GET_EMERGENCY_LEN)
        crc_field = utils.flatscan_chk_field_build(sync_field + GET_EMERGENCY_CMD)
        self.flatscan_serial.write(sync_field + GET_EMERGENCY_CMD + crc_field)

        msg = self.__get_msg(MSG_EMERGENCY_CMD)
        if DEBUG:
            self.log_action("get parameters returned", msg)
        return utils.flatscan_parse_emergency_msg(msg)

    def get_parameters(self):
        """
        Get FLATSCAN parameters

        :return: dictionary that stores the received parameters configuration and verification bits
        """
        if DEBUG:
            self.log_action("get parameters called", 0)
        sync_field = utils.flatscan_sync_field_build(GET_PARAMETERS_LEN)
        crc_field = utils.flatscan_chk_field_build(sync_field + GET_PARAMETERS_CMD)
        self.flatscan_serial.write(sync_field + GET_PARAMETERS_CMD + crc_field)
        print(sync_field + GET_PARAMETERS_CMD + crc_field)
        msg = self.__get_msg(MSG_SEND_PARAMETERS_CMD)
        if msg is None:
            self.handle_timeout("time out from set params")
            return
        if DEBUG:
            self.log_action("get parameters returned", msg)
        return utils.flatscan_parse_parameters_msg(msg)

    def get_facet(self):
        """
        Get FLATSCAN facet number
        :return:
        For HS mode: Reference of the current mirror facet (1, 2, 3, 4).
        For HD mode: 5.
        """
        params = self.get_parameters()
        self.parameters_state = params
        return params['facet_number_field']

    def get_identity(self):
        """
        Get FLATSCAN identity

        :return: dictionary of FLATSCAN product part number (BEA TOF), software version, software revision,
        software prototype, CAN number of the detector (BEA serial number)
        """

        sync_field = utils.flatscan_sync_field_build(GET_IDENTITY_LEN)
        crc_field = utils.flatscan_chk_field_build(sync_field + GET_IDENTITY_CMD)
        self.flatscan_serial.write(sync_field + GET_IDENTITY_CMD + crc_field)

        msg = self.__get_msg(MSG_SEND_IDENTITY_CMD)
        if DEBUG:
            self.log_action("get identity returned", msg)
        return utils.flatscan_parse_identity_msg(msg)

    def get_mdi(self):
        """
        Get FLATSCAN MDI (measured distance information)

        :return: dictionary of CAN number, mdi frames counter, internal temperature, reference of the
        current mirror facet, measured distances, and measured remissions
        """

        sync_field = utils.flatscan_sync_field_build(GET_MEASUREMENTS_LEN)
        data_field = b'\x00'
        crc_field = utils.flatscan_chk_field_build(sync_field + GET_MEASUREMENTS_CMD + data_field)
        self.flatscan_serial.write(sync_field + GET_MEASUREMENTS_CMD + data_field + crc_field)

        msg = self.__get_msg(MSG_MDI_CMD)
        if DEBUG:
            self.log_action("mdi Information", msg)
        if msg==None:
            return
        return utils.flatscan_parse_mdi_msg(msg, self.parameters_state)

    def get_can(self):
        """
        Get CAN number of the detector(BEA serial number)

        :return: CAN number
        """
        identity = self.get_identity()
        return identity['CAN_number']

    def reset_mdi_counter(self):
        """
        reset MDI frames counter to the default value of 1

        :return: boolean ACK
        """

        sync_field = utils.flatscan_sync_field_build(RESET_MDI_COUNTER_LEN)
        crc_field = utils.flatscan_chk_field_build(sync_field + RESET_MDI_COUNTER_CMD)
        self.flatscan_serial.write(sync_field + RESET_MDI_COUNTER_CMD + crc_field)
        if DEBUG:
            self.log_action("reset mdi counter", 0)
        return self.__get_ack(ACK_RESET_MDI_COUNTER)

    def reset_heartbeat_counter(self):
        """
        reset HEARTBEAT frames counter to the default value of 1

        :return: boolean ACK
        """

        sync_field = utils.flatscan_sync_field_build(RESET_HEARTBEAT_COUNTER_LEN)
        crc_field = utils.flatscan_chk_field_build(sync_field + RESET_HEARTBEAT_COUNTER_CMD)
        self.flatscan_serial.write(sync_field + RESET_HEARTBEAT_COUNTER_CMD + crc_field)
        if DEBUG:
            self.log_action("reset heartbeat_counter", 0)
        return self.__get_ack(ACK_RESET_HEARTBEAT_COUNTER)

    def reset_emergency_counter(self):
        """
        reset EMERGENCY frames counter to the default value of 1

        :return: boolean ACK
        """

        sync_field = utils.flatscan_sync_field_build(RESET_EMERGENCY_COUNTER_LEN)
        crc_field = utils.flatscan_chk_field_build(sync_field + RESET_EMERGENCY_COUNTER_CMD)
        self.flatscan_serial.write(sync_field + RESET_EMERGENCY_COUNTER_CMD + crc_field)
        if DEBUG:
            self.log_action("reset emergency counter", 0)
        return self.__get_ack(ACK_RESET_EMERGENCY_COUNTER)

    def register_heartbeat_handler(self, heartbeat_handler):
        self.read_thread.register_heartbeat_handler(heartbeat_handler)

    def register_emergency_handler(self, emergency_handler):
        self.read_thread.register_emergency_handler(emergency_handler)

    def save_parameters(self, file_path):
        """
        save current parameters state to the file

        :param file_path: file path to save
        :return: true if successfully save, otherwise false
        """
        try:
            file = open(file_path, 'w')
            file.write(json.dumps(self.parameters_state))
            file.close()
        except OSError:
            return False
        return True

    def load_parameters(self, file_path):
        """
        load parameters state from file and set the parameters to the FLATSCAN sensor

        :param file_path: file path to load
        :return: verification bits that confirms if the parameters configured by is correct.
            -1 if failed to load file
        """
        try:
            file = open(file_path, 'r')
            content = file.read()
            self.parameters_state = json.loads(content)
            param_to_set = self.parameters_state.copy()
            param_to_set.pop('verification_bits')
            file.close()
        except OSError:
            return False
        return self.set_parameters(**param_to_set)

    def __get_msg(self, msg_cmd):
        """
        private method used to get the last message from buffers
        :param msg_cmd: message cmd field (type of message)
        :return: the newest message with the given msg_cmd
        """

        self.conditions[msg_cmd].acquire()
        timeout = self.conditions[msg_cmd].wait(3)
        if timeout:
            msg = self.buffers[msg_cmd][-1]
            self.conditions[msg_cmd].release()
            return msg
        else:
            print("timeout")

    def __get_ack(self, ack_cmd):
        """
        private method used to check if received ACK within the timeout time
        :param ack_cmd: type of ack
        :return: true if received ACK within the timeout time, otherwise false
        """

        self.conditions[ack_cmd].acquire()
        res = self.conditions[ack_cmd].wait(ACK_TIMEOUT_TIME)
        self.conditions[ack_cmd].release()
        return res
