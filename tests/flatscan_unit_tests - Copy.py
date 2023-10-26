import unittest
import api.flatscan_utils as flatscan_utils
from api.flatscan_parameters import *

from tests import test_data_generator

heartbeat_example1 = b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1c\x00\x46\x21'
heartbeat_example2 = b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1d\x00\x05\x8e'
heartbeat_example3 = b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1e\x00\x19\xef'
heartbeat_example4 = b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1f\x00\x5a\x40'


class Test(unittest.TestCase):

    def test_invalid_message(self):
        self.assertFalse(flatscan_utils.flatscan_message_validate(b'\xbe\xa0\x12\x34\x32\x43'))

        # invalid heartbeat with wrong chk
        self.assertFalse(flatscan_utils.flatscan_message_validate(b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64'
                                                                  b'\xc3\xaf\xa0\x52\x00\x1c\x00\x46\x28'))

        wrong_cmd = b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x94\xc3\xaf\xa0\x52\x00\x1c\x00'
        chk = flatscan_utils.flatscan_chk_field_build(wrong_cmd)
        wrong_cmd = wrong_cmd + chk
        self.assertFalse(flatscan_utils.flatscan_message_validate(wrong_cmd))

        wrong_sync = b'\xbe\xa0\x12\x34\x02\x10\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1c\x00'
        chk = flatscan_utils.flatscan_chk_field_build(wrong_sync)
        wrong_sync = wrong_sync + chk
        self.assertFalse(flatscan_utils.flatscan_message_validate(wrong_sync))

    def test_valid_message(self):
        # valid heartbeat
        self.assertTrue(flatscan_utils.flatscan_message_validate(heartbeat_example1))

    def test_heartbeat_parsing(self):
        info = flatscan_utils.flatscan_parse_heartbeat_msg(
            b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\x00\x00\x00\x00\x01\x00\x46\x21')
        self.assertEqual(info[0], 0)
        self.assertEqual(info[1], 1)
        info = flatscan_utils.flatscan_parse_heartbeat_msg(
            b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\x02\x00\x0a\x00\x01\x0e\x46\x21')
        self.assertEqual(info[0], 655362)
        self.assertEqual(info[1], 3585)

    def test_identity_parsing(self):
        msg = test_data_generator.generate_flatscan_send_identity()
        self.assertTrue(flatscan_utils.flatscan_message_validate(msg))
        info = flatscan_utils.flatscan_parse_identity_msg(msg)
        self.assertEqual(info['product_part_number'], 1)
        self.assertEqual(info['software_version'], 2)
        self.assertEqual(info['software_revision'], 3)
        self.assertEqual(info['software_prototype'], 4)
        self.assertEqual(info['CAN_number'], 5)
        # TODO: actual message testing

    def test_emergency_parsing(self):
        emergency_sync = b'\xbe\xa0\x12\x34\x02\x19\x00\x02\x00\x00\x00'
        cmd = b'\x6e\xc3'
        can_number = b'\x01\x00\x00\x00'
        cntr = b'\x02\x00'
        rs485_error = RS485_INTEGRITY_FAIL2  # Hardware failure in the RS485 module
        measure_head_error = MEASURE_HEAD_HARDWARE_FAIL1
        # with CAN and CNTR
        msg = emergency_sync + cmd + can_number + cntr + rs485_error + measure_head_error
        chk = flatscan_utils.flatscan_chk_field_build(msg)
        msg = msg + chk
        self.assertTrue(flatscan_utils.flatscan_message_validate(msg))
        info = flatscan_utils.flatscan_parse_emergency_msg(msg)
        self.assertEqual(info['CAN_number'], 1)
        self.assertEqual(info['emergency_counter'], 2)
        self.assertEqual(info['RS485_error_code'], RS485_INTEGRITY_FAIL2)
        self.assertEqual(info['measuring_head_error_code'], MEASURE_HEAD_HARDWARE_FAIL1)

        # without CAN and cntr
        emergency_sync = b'\xbe\xa0\x12\x34\x02\x13\x00\x02\x00\x00\x00'
        msg = emergency_sync + cmd + rs485_error + measure_head_error
        chk = flatscan_utils.flatscan_chk_field_build(msg)
        msg = msg + chk
        self.assertTrue(flatscan_utils.flatscan_message_validate(msg))
        info = flatscan_utils.flatscan_parse_emergency_msg(msg)
        self.assertEqual(info['RS485_error_code'], RS485_INTEGRITY_FAIL2)
        self.assertEqual(info['measuring_head_error_code'], MEASURE_HEAD_HARDWARE_FAIL1)

        # TODO: actual message testing

    def test_parameter_parsing(self):
        msg = test_data_generator.generate_flatscan_send_parameters();
        self.assertTrue(flatscan_utils.flatscan_message_validate(msg))
        info = flatscan_utils.flatscan_parse_parameters_msg(msg)
        self.assertEqual(info['verification_bits'], 1347141632)
        self.assertEqual(info['temperature'], 1)
        self.assertEqual(info['detection_field_mode'], 1)
        self.assertEqual(info['sensitivity'], 3)
        self.assertEqual(info['num_spots'], 4)
        self.assertEqual(info['angle_first'], 5)
        self.assertEqual(info['angle_last'], 6)
        self.assertEqual(info['can_and_frame_counter'], 1)
        self.assertEqual(info['heartbeat_period'], 7)
        self.assertEqual(info['facet_number_field'], 1)
        self.assertEqual(info['averaging'], 2)

    def test_state_to_byte(self):
        info={'verification_bits': 1347141632, 'temperature':1, 'detection_field_mode':1,
              'sensitivity':3, 'num_spots':4, 'angle_first':5, 'angle_last':6, 'can_and_frame_counter':1,
              'heartbeat_period': 7, 'facet_number_field':1, 'averaging':2, 'mdi_info':2}

        byte=flatscan_utils.flatscan_parameters_state_to_bytes(info)
        msg=test_data_generator.generate_flatscan_send_parameters()[12:];
        #self.assertEqual(msg,byte)
    def test_mdi_parsing(self):
        cmd = b'\x5b\xc3'
        # no data
        sync = flatscan_utils.flatscan_sync_field_build(15)
        chk = flatscan_utils.flatscan_chk_field_build(sync + cmd)
        msg = sync + cmd + chk
        self.assertTrue(flatscan_utils.flatscan_message_validate(msg))
        required_states = {'can_and_frame_counter': 0, 'temperature': 0, 'facet_number_field': 0, 'mdi_info': 0,
                           'num_spots': 0}
        flatscan_utils.flatscan_parse_mdi_msg(msg, required_states)
        required_states = {'can_and_frame_counter': 1, 'temperature': 1, 'facet_number_field': 1, 'mdi_info': 2,
                           'num_spots': 4}
        msg=test_data_generator.generate_send_mdi()
        self.assertTrue(flatscan_utils.flatscan_message_validate(msg))
        info = flatscan_utils.flatscan_parse_mdi_msg(msg, required_states)
        self.assertEqual(info['CAN_number'], 1)
        self.assertEqual(info['mdi_frames_counter'], 2)
        self.assertEqual(info['temperature'], 3)
        self.assertEqual(info['facet'], 4)
        self.assertEqual(info['distances'], [1, 2, 3, 4])
        self.assertEqual(info['remissions'], [5, 6, 7, 8])
        info = flatscan_utils.flatscan_parse_mdi_msg(msg, [])
        self.assertEqual(info, None)



    def test_chk_build(self):
        message_without_chk = b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1c\x00'
        self.assertEqual(flatscan_utils.flatscan_chk_field_build(message_without_chk), b'\x46\x21')
        message_without_chk = b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1d\x00'
        self.assertEqual(flatscan_utils.flatscan_chk_field_build(message_without_chk), b'\x05\x8e')
        message_without_chk = b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00\x64\xc3\xaf\xa0\x52\x00\x1e\x00'
        self.assertEqual(flatscan_utils.flatscan_chk_field_build(message_without_chk), b'\x19\xef')

    def test_sync_build(self):
        heartbeat_sync = flatscan_utils.flatscan_sync_field_build(21)
        correct = b'\xbe\xa0\x12\x34\x02\x15\x00\x02\x00\x00\x00'
        self.assertEqual(heartbeat_sync, correct);
        identity_sync = flatscan_utils.flatscan_sync_field_build(27)
        correct = b'\xbe\xa0\x12\x34\x02\x1b\x00\x02\x00\x00\x00'
        self.assertEqual(identity_sync, correct);
        random_sync = flatscan_utils.flatscan_sync_field_build(56)
        correct = b'\xbe\xa0\x12\x34\x02\x38\x00\x02\x00\x00\x00'
        self.assertEqual(random_sync, correct);


if __name__ == '__main__':
    unittest.main()
