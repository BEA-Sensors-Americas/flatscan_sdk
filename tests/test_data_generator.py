import api.flatscan_utils as utils


def generate_flatscan_send_identity():
    identity_sync = b'\xbe\xa0\x12\x34\x02\x1b\x00\x02\x00\x00\x00'
    cmd = b'\x5a\xc3'
    part_number = b'\x01\x00\x00\x00'
    software_version = b'\x02'
    software_revision = b'\x03'
    software_prototype = b'\x04'
    can_number = b'\x05\x00\x00\x00\x00'
    chk = utils.flatscan_chk_field_build(identity_sync + cmd + part_number
                                         + software_version + software_revision + software_prototype
                                         + can_number)
    receive_msg = identity_sync + cmd + part_number + software_version + software_revision + software_prototype \
                  + can_number + chk
    return receive_msg


def generate_flatscan_send_parameters():
    parameter_sync = b'\xbe\xa0\x12\x34\x02\x2b\x00\x02\x00\x00\x00'
    cmd = b'\x54\xc3'
    verification_bits = b'\x00\xc0\x4b\x50'  # 504bc000
    communication_charge = b'\x02\x00\x00'
    cnt_field = b'\x01'
    information_in_mdi = b'\x02'
    detection_mode = b'\x01'
    sensitivity = b'\x03\x00\x00\x00'  # pad 3
    num_of_spots = b'\x04\x00\x00\x00\x00\x00'  # pad 4
    angle_first = b'\x05\x00'
    angle_last = b'\x06\x00'
    can_enable = b'\x01'
    heartbeat_period = b'\x07'
    facet_number = b'\x01'
    averaging_setting = b'\x02'
    msg = parameter_sync + cmd + verification_bits + communication_charge + cnt_field \
          + information_in_mdi + detection_mode + sensitivity + num_of_spots \
          + angle_first + angle_last + can_enable + heartbeat_period + facet_number + averaging_setting
    chk = utils.flatscan_chk_field_build(msg)
    return msg + chk


def generate_send_mdi():
    cmd = b'\x5b\xc3'
    can = b'\x01\x00\x00\x00'
    cntr = b'\x02\x00'
    temperature = b'\x03\x00'
    facet = b'\x04'

    distances = b'\x01\x00\x02\x00\x03\x00\x04\x00'
    remission = b'\x05\x00\x06\x00\x07\x00\x08\x00'
    sync = utils.flatscan_sync_field_build(40)
    msg = sync + cmd + can + cntr + temperature + facet + distances + remission
    chk = utils.flatscan_chk_field_build(msg)
    msg = msg + chk
    return msg


def generate_state(can_and_frame_counter, temperature, facet_number_field, mdi_info, num_spots):
    return {'can_and_frame_counter': can_and_frame_counter, 'temperature': temperature,
            'facet_number_field': facet_number_field, 'mdi_info': mdi_info,
            'num_spots': num_spots}
