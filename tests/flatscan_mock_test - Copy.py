from mock_serial import MockSerial
from serial import Serial
from collections import deque
import unittest
import api.flatscan_api as api
import api.flatscan_utils as utils
from api.flatscan_parameters import *
from tests import test_data_generator
import logging, sys
import time



class TestMock(unittest.TestCase):

    def test_stub(self):
        device = MockSerial()
        device.open()
        serial = Serial(device.port)
        stub = device.stub(
            receive_bytes=b'123',
            send_bytes=b'456'
        )
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(levelname)s - %(message)s"
        )
        serial.write(b'123')
        assert serial.read(3) == b'456'

        assert stub.called
        assert stub.calls == 1

        serial.close()
        device.close()

    def test_get_identity(self):
        device = MockSerial()
        device.open()
        serial = Serial(device.port)
        sync = utils.flatscan_sync_field_build(15)
        cmd = b'\x5a\xc3'
        crc = utils.flatscan_chk_field_build(sync + cmd)
        get_msg = sync + cmd + crc
        receive_msg = test_data_generator.generate_flatscan_send_identity()
        stub1 = device.stub(
            receive_bytes=get_msg,
            send_bytes=receive_msg
        )
        sync = utils.flatscan_sync_field_build(15)
        cmd = b'\x54\xc3'
        crc = utils.flatscan_chk_field_build(sync + cmd)
        get_msg = sync + cmd + crc
        receive_msg = test_data_generator.generate_flatscan_send_parameters()
        stub2 = device.stub(
            receive_bytes=get_msg,
            send_bytes=receive_msg
        )
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(levelname)s - %(message)s"
        )
        flatscan = api.Flatscan(True, serial)
        flatscan.enable_log();
        info = flatscan.get_identity()
        assert stub1.called
        assert stub1.calls == 1

        self.assertEqual(info['product_part_number'], 1)
        self.assertEqual(info['software_version'], 2)
        self.assertEqual(info['software_revision'], 3)
        self.assertEqual(info['software_prototype'], 4)
        self.assertEqual(info['CAN_number'], 5)
        flatscan.read_thread.stop()
        flatscan.export_log("abc.txt","efg.txt")


        device.close()
        serial.close()

    def test_get_parameter(self):
        device = MockSerial()
        device.open()
        serial = Serial(device.port)
        sync = utils.flatscan_sync_field_build(15)
        cmd = b'\x54\xc3'
        crc = utils.flatscan_chk_field_build(sync + cmd)
        get_msg = sync + cmd + crc
        receive_msg= test_data_generator.generate_flatscan_send_parameters()
        stub1 = device.stub(
            receive_bytes=get_msg,
            send_bytes=receive_msg
        )
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(levelname)s - %(message)s"
        )
        flatscan = api.Flatscan(True, serial)

        info = flatscan.parameters_state
        assert stub1.called
        assert stub1.calls == 1

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
        flatscan.read_thread.stop()
        flatscan.export_log("asdads.txt")
        device.close()
        serial.close()

    def test_get_mdi(self):
        device = MockSerial()
        device.open()
        serial = Serial(device.port)
        sync = utils.flatscan_sync_field_build(16)
        cmd = b'\x5b\xc3'
        data_field= b'\x00'
        crc = utils.flatscan_chk_field_build(sync + cmd + data_field)
        get_msg = sync + cmd + data_field + crc
        required_states = {'can_and_frame_counter': 1, 'temperature': 1, 'facet_number_field': 1, 'mdi_info': 2,
                           'num_spots': 4}
        receive_msg = test_data_generator.generate_send_mdi()
        stub1 = device.stub(
            receive_bytes=get_msg,
            send_bytes=receive_msg
        )
        sync = utils.flatscan_sync_field_build(15)
        cmd = b'\x54\xc3'
        crc = utils.flatscan_chk_field_build(sync + cmd)
        get_msg = sync + cmd  + crc
        receive_msg = test_data_generator.generate_flatscan_send_parameters()
        stub2 = device.stub(
            receive_bytes=get_msg,
            send_bytes=receive_msg
        )
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(levelname)s - %(message)s"
        )
        flatscan = api.Flatscan(True, serial)
        assert stub2.called
        assert stub2.calls == 1
        info=flatscan.get_mdi()
        self.assertEqual(info['CAN_number'], 1)
        self.assertEqual(info['mdi_frames_counter'], 2)
        self.assertEqual(info['temperature'], 3)
        self.assertEqual(info['facet'], 4)
        self.assertEqual(info['distances'], [1, 2, 3, 4])
        self.assertEqual(info['remissions'], [5, 6, 7, 8])
        flatscan.read_thread.stop()
        device.close()
        serial.close()


