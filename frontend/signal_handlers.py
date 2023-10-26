import frontend.variable_enums as var
import frontend.validators as validators
import frontend.popup as popup
import frontend.api_calls as api
from frontend.api_calls import *
from datetime import datetime
from PyQt6 import QtWidgets
import frontend.parser as parser
import frontend.colors as colors

main_ui = None
sensor_params = None
main_window = None
renderer = None


def set_window_and_sensor_params(main_ui_, sensor_params_, main_window_, renderer_):
    global main_ui, sensor_params, main_window, renderer
    main_window = main_window_
    main_ui = main_ui_
    sensor_params = sensor_params_
    renderer = renderer_


def register_handlers():
    main_ui.comboBox_baud_rate.currentIndexChanged.connect(baud_rate_selection)
    main_ui.comboBox_com_port.currentIndexChanged.connect(com_port_selection)
    main_ui.comboBox_optimization.currentIndexChanged.connect(optimization_selection)
    main_ui.comboBox_information_in_mdi.currentIndexChanged.connect(information_in_mdi_selection)
    main_ui.comboBox_averaging.currentIndexChanged.connect(averaging_selection)
    main_ui.comboBox_detection_field_mode.currentIndexChanged.connect(detection_field_mode_selection)

    main_ui.pushButton_enable_can.clicked.connect(enable_can)
    main_ui.pushButton_enable_ctn.clicked.connect(enable_ctn)
    main_ui.pushButton_enable_facet.clicked.connect(enable_facet)

    main_ui.pushButton_retrieve_params.clicked.connect(retrieve_params)
    main_ui.pushButton_apply_params.clicked.connect(apply_params)
    main_ui.pushButton_import_params.clicked.connect(import_params)
    main_ui.pushButton_save_params.clicked.connect(save_params)
    main_ui.pushButton_export_log.clicked.connect(export_log)

    main_ui.pushButton_connect.clicked.connect(connect)
    main_ui.pushButton_get_identity.clicked.connect(get_identity)

    # main_ui.pushButton_display_measurements.clicked.connect(display_measurements)

    main_ui.lineEdit_angle_first.editingFinished.connect(angle_first_input)
    main_ui.lineEdit_angle_last.editingFinished.connect(angle_last_input)
    main_ui.lineEdit_spots_number.editingFinished.connect(spots_number_input)


def baud_rate_selection():
    selected_text = main_ui.comboBox_baud_rate.currentText()
    if selected_text == '57600':
        sensor_params.set_baud_rate(var.BAUD_RATE_57600)
    elif selected_text == '115200':
        sensor_params.set_baud_rate(var.BAUD_RATE_115200)
    elif selected_text == '230400':
        sensor_params.set_baud_rate(var.BAUD_RATE_230400)
    elif selected_text == '460800':
        sensor_params.set_baud_rate(var.BAUD_RATE_460800)
    elif selected_text == '921600':
        sensor_params.set_baud_rate(var.BAUD_RATE_921600)
    add_text_to_browser(var.INFO, 'Baud rate selected: ' + selected_text)


def com_port_selection():
    selected_port = main_ui.comboBox_com_port.currentText()
    sensor_params.set_com_port(int(selected_port))
    add_text_to_browser(var.INFO, 'Com port selected: ' + selected_port)


def optimization_selection():
    selected_optimization = main_ui.comboBox_optimization.currentText()
    if selected_optimization == '0':
        sensor_params.set_optimization(var.OPTIMIZATION_NONE)
    elif selected_optimization == '0-2.5m':
        sensor_params.set_optimization(var.OPTIMIZATION_1)
    elif selected_optimization == '0-3m':
        sensor_params.set_optimization(var.OPTIMIZATION_2)
    elif selected_optimization == '0-3.5m':
        sensor_params.set_optimization(var.OPTIMIZATION_3)
    elif selected_optimization == '>3.5m':
        sensor_params.set_optimization(var.OPTIMIZATION_4)
    add_text_to_browser(var.INFO, 'Optimization selected: ' + selected_optimization)


def information_in_mdi_selection():
    selected_info = main_ui.comboBox_information_in_mdi.currentText()
    if selected_info == 'Distances Only':
        sensor_params.set_information_in_mdi(var.INFORMATION_IN_MID_DISTANCES)
    elif selected_info == 'Remissions Only':
        sensor_params.set_information_in_mdi(var.INFORMATION_IN_MID_REMISSIONS)
    else:
        sensor_params.set_information_in_mdi(var.INFORMATION_IN_MID_DISTANCES_AND_REMISSIONS)
    add_text_to_browser(var.INFO, 'Information in mdi selected: ' + selected_info)


def averaging_selection():
    selected_averaging = main_ui.comboBox_averaging.currentText()
    if selected_averaging == 'No Averaging':
        sensor_params.set_averaging(var.AVERAGING_NONE)
    elif selected_averaging == '3 Points':
        sensor_params.set_averaging(var.AVERAGING_3_POINTS)
    elif selected_averaging == '3 Points + 2 Neighbors':
        sensor_params.set_averaging(var.AVERAGING_3_POINTS_AND_TWO_NEIGHBORS)
    elif selected_averaging == '5 Points':
        sensor_params.set_averaging(var.AVERAGING_5_POINTS)
    elif selected_averaging == '5 Points + 2 Neighbors':
        sensor_params.set_averaging(var.AVERAGING_5_POINTS_AND_TWO_NEIGHBORS)
    add_text_to_browser(var.INFO, 'Averaging selected: ' + selected_averaging)


def detection_field_mode_selection():
    selected_mode = main_ui.comboBox_detection_field_mode.currentText()
    # Do extra check when changing to HD since HD mode has more restriction on spots number.
    if selected_mode == 'HD':
        if not validators.validate_detection_field(sensor_params.angle_first, sensor_params.angle_last,
                                                   sensor_params.spots_number,
                                                   var.DETECTION_FIELD_MODE_HD):
            main_ui.comboBox_detection_field_mode.setCurrentText('HS')
            dlg = popup.CustomMessageBox(var.MESSAGE, var.MSG_INVALID_DETECTION_FIELD_MODE)
            add_text_to_browser(var.ERROR, var.MSG_INVALID_DETECTION_FIELD_MODE)
            dlg.exec()
            return
    if selected_mode == 'HS':
        sensor_params.set_detection_field_mode(var.DETECTION_FIELD_MODE_HS)
    else:
        sensor_params.set_detection_field_mode(var.DETECTION_FIELD_MODE_HD)
    add_text_to_browser(var.INFO, 'Detection field mode selected: ' + selected_mode)


def initialize_all_push_buttons():
    main_ui.pushButton_enable_can.setCheckable(True)
    main_ui.pushButton_enable_can.toggle()
    main_ui.pushButton_enable_ctn.setCheckable(True)
    main_ui.pushButton_enable_ctn.toggle()
    main_ui.pushButton_enable_facet.setCheckable(True)
    main_ui.pushButton_enable_facet.toggle()


def initialize_default_text():
    main_ui.lineEdit_angle_first.setText(str(sensor_params.angle_first))
    main_ui.lineEdit_angle_last.setText(str(sensor_params.angle_last))
    main_ui.lineEdit_spots_number.setText(str(sensor_params.spots_number))


def initialize_connection_settings():
    main_ui.comboBox_baud_rate.setCurrentText(str(sensor_params.baud_rate))
    main_ui.comboBox_com_port.setCurrentText(str(sensor_params.com_port))


def enable_can():
    sensor_params.set_enable_can(main_ui.pushButton_enable_can.isChecked())
    add_text_to_browser(var.INFO, 'Enable CAN is set to: ' + str(main_ui.pushButton_enable_can.isChecked()))


def enable_ctn():
    sensor_params.set_enable_ctn(main_ui.pushButton_enable_ctn.isChecked())
    add_text_to_browser(var.INFO, 'Enable CTN is set to: ' + str(main_ui.pushButton_enable_ctn.isChecked()))


def enable_facet():
    sensor_params.set_enable_facet(main_ui.pushButton_enable_facet.isChecked())
    add_text_to_browser(var.INFO, 'Enable FACET is set to: ' + str(main_ui.pushButton_enable_facet.isChecked()))


def retrieve_params():
    try:
        msg = api.get_parameter(sensor_params)

        # Apply the retrieved params to frontend.
        print('Sensor param')
        print(str(sensor_params))
        main_ui.lineEdit_angle_first.setText(str(sensor_params.angle_first))
        main_ui.lineEdit_angle_last.setText(str(sensor_params.angle_last))
        main_ui.lineEdit_spots_number.setText(str(sensor_params.spots_number))
        main_ui.pushButton_enable_ctn.setChecked(sensor_params.enable_ctn)
        main_ui.pushButton_enable_can.setChecked(sensor_params.enable_can)
        main_ui.pushButton_enable_facet.setChecked(sensor_params.enable_facet)

        if sensor_params.detection_field_mode == 0:
            main_ui.comboBox_detection_field_mode.setCurrentText("HS")
        else:
            main_ui.comboBox_detection_field_mode.setCurrentText("HD")

        if sensor_params.optimization == 0:
            main_ui.comboBox_optimization.setCurrentText("0m")
        elif sensor_params.optimization == 1:
            main_ui.comboBox_optimization.setCurrentText("0-2.5m")
        elif sensor_params.optimization == 2:
            main_ui.comboBox_optimization.setCurrentText("0-3m")
        elif sensor_params.optimization == 3:
            main_ui.comboBox_optimization.setCurrentText("0-3.5m")
        else:
            main_ui.comboBox_optimization.setCurrentText(">3.5m")

        if sensor_params.information_in_mdi == 0:
            main_ui.comboBox_information_in_mdi.setCurrentText("Distances Only")
        elif sensor_params.information_in_mdi == 1:
            main_ui.comboBox_information_in_mdi.setCurrentText("Remissions Only")
        else:
            main_ui.comboBox_information_in_mdi.setCurrentText("Distances & Remissions")

        if sensor_params.averaging == 0:
            main_ui.comboBox_averaging.setCurrentText("No Averaging")
        elif sensor_params.averaging == 1:
            main_ui.comboBox_averaging.setCurrentText("3 Points")
        elif sensor_params.averaging == 2:
            main_ui.comboBox_averaging.setCurrentText("3 Points + 2 Neighbors")
        elif sensor_params.averaging == 3:
            main_ui.comboBox_averaging.setCurrentText("5 Points")
        else:
            main_ui.comboBox_averaging.setCurrentText("5 Points + 2 Neighbors")

        add_text_to_browser(var.INFO, "Retrieve paras: " + msg)
    except Exception as e:
        if str(e).startswith("'NoneType' object has no attribute"):
            add_text_to_browser(var.ERROR, var.SENSOR_NOT_CONNECTED)
        else:
            add_text_to_browser(var.ERROR, str(e))


def apply_params():
    try:
        msg = api.set_parameter(sensor_params)
        add_text_to_browser(var.INFO, "Apply params to sensor: " + parser.parse_set_parameters_return(msg))
    except Exception as e:
        if str(e).startswith("'NoneType' object has no attribute"):
            add_text_to_browser(var.ERROR, var.SENSOR_NOT_CONNECTED)
        else:
            add_text_to_browser(var.ERROR, str(e))


def import_params():
    try:
        file_path = QtWidgets.QFileDialog.getOpenFileName(main_window, 'Select File')
        _ = read_params_from_file(file_path[0])
        retrieve_params()
        add_text_to_browser(var.INFO, "Import params: " + file_path[0])
    except Exception as e:
        add_text_to_browser(var.ERROR, str(e))


def export_log():
    try:
        file_path = QtWidgets.QFileDialog.getSaveFileName(main_window, 'Export log')
        _ = api.export_log(file_path[0])
        add_text_to_browser(var.INFO, "Export log: " + file_path[0])
    except Exception as e:
        add_text_to_browser(var.ERROR, str(e))


from api.flatscan_api import *


def connect():
    try:
        f = Flatscan(sensor_params.com_port, baudrate=sensor_params.baud_rate)
        f.register_emergency_handler(flatscan_emergency_handler)
        api.set_flatscan(f)
        add_text_to_browser(var.INFO, "Connection to sensor is established successfully")

        # Fetch settings.
        retrieve_params()
        add_text_to_browser(var.INFO, "Sensor settings fetched successfully")
        renderer.start_reading_mdi()
    except Exception as e:
        add_text_to_browser(var.ERROR, str(e))


def get_identity():
    try:
        msg = api.get_identity()
        add_text_to_browser(var.INFO, "Sensor identity: " + str(msg))
    except Exception as e:
        add_text_to_browser(var.ERROR, str(e))


def save_params():
    try:
        file_path = QtWidgets.QFileDialog.getSaveFileName(main_window, 'Save File')
        msg = save_params_to_file(file_path[0])
        add_text_to_browser(var.INFO, "Save params: " + file_path[0])
    except Exception as e:
        add_text_to_browser(var.ERROR, str(e))


def angle_first_input():
    if not main_ui.lineEdit_angle_first.isModified():
        return
    main_ui.lineEdit_angle_first.blockSignals(True)
    angle_first_str = main_ui.lineEdit_angle_first.text()
    try:
        angle_first = float(angle_first_str)
        # Automatic round to two decimals.
        angle_first = round(angle_first, 2)
        valid = validators.validate_detection_field(angle_first, sensor_params.angle_last, sensor_params.spots_number,
                                                    sensor_params.detection_field_mode)
        if valid:
            add_text_to_browser(var.INFO, 'Angle first changed to: ' + str(angle_first))
            sensor_params.set_angle_first(angle_first)
            main_ui.lineEdit_angle_first.setText(str(angle_first))
        else:
            dlg = popup.CustomMessageBox(var.MESSAGE, var.MSG_INVALID_ANGLE_FIRST_INPUT)
            add_text_to_browser(var.ERROR, var.MSG_INVALID_ANGLE_FIRST_INPUT)
            dlg.exec()
            # Restore GUI to last correct setting.
            main_ui.lineEdit_angle_first.setText(str(sensor_params.angle_first))
    except ValueError:
        dlg = popup.CustomMessageBox(var.MESSAGE, var.MSG_INVALID_ANGLE_FIRST_INPUT)
        add_text_to_browser(var.ERROR, var.MSG_INVALID_ANGLE_FIRST_INPUT)
        dlg.exec()
        add_text_to_browser(var.ERROR, 'Angle first must be float between 0 and angle last')
        # Restore GUI to last correct setting.
        main_ui.lineEdit_angle_first.setText(str(sensor_params.angle_first))
    finally:
        main_ui.lineEdit_angle_first.blockSignals(False)


def angle_last_input():
    if not main_ui.lineEdit_angle_last.isModified():
        return
    main_ui.lineEdit_angle_last.blockSignals(True)
    angle_last_str = main_ui.lineEdit_angle_last.text()

    try:
        angle_last = float(angle_last_str)
        # Automatic round to two decimals.
        angle_last = round(angle_last, 2)
        valid = validators.validate_detection_field(sensor_params.angle_first, angle_last, sensor_params.spots_number,
                                                    sensor_params.detection_field_mode)
        if valid:
            add_text_to_browser(var.INFO, 'Angle last changed to: ' + str(angle_last))
            sensor_params.set_angle_last(angle_last)
            main_ui.lineEdit_angle_last.setText(str(angle_last))
        else:
            dlg = popup.CustomMessageBox(var.MESSAGE, var.MSG_INVALID_ANGLE_LAST_INPUT)
            add_text_to_browser(var.ERROR, var.MSG_INVALID_ANGLE_LAST_INPUT)
            dlg.exec()
            # Restore GUI to last correct setting.
            main_ui.lineEdit_angle_last.setText(str(sensor_params.angle_last))
    except ValueError:
        dlg = popup.CustomMessageBox(var.MESSAGE, var.MSG_INVALID_ANGLE_LAST_INPUT)
        add_text_to_browser(var.ERROR, var.MSG_INVALID_ANGLE_LAST_INPUT)
        dlg.exec()
        add_text_to_browser(var.ERROR, 'Angle last must be float between angle first and 108')
        # Restore GUI to last correct setting.
        main_ui.lineEdit_angle_last.setText(str(sensor_params.angle_last))
    finally:
        main_ui.lineEdit_angle_last.blockSignals(False)


def spots_number_input():
    if not main_ui.lineEdit_spots_number.isModified():
        return
    main_ui.lineEdit_spots_number.blockSignals(True)
    spots_number_str = main_ui.lineEdit_spots_number.text()
    try:
        spots_number = int(spots_number_str)
        valid = validators.validate_detection_field(sensor_params.angle_first, sensor_params.angle_last, spots_number,
                                                    sensor_params.detection_field_mode)
        if valid:
            add_text_to_browser(var.INFO, 'Spots number changed to: ' + spots_number_str)
            sensor_params.set_spots_number(spots_number)
        else:
            if sensor_params.detection_field_mode == var.DETECTION_FIELD_MODE_HS:
                dlg = popup.CustomMessageBox(var.MESSAGE, var.MSG_INVALID_SPOTS_NUMBER_IN_HS)
                add_text_to_browser(var.ERROR, var.MSG_INVALID_SPOTS_NUMBER_IN_HS)
            else:
                dlg = popup.CustomMessageBox(var.MESSAGE, var.MSG_INVALID_SPOTS_NUMBER_IN_HD)
                add_text_to_browser(var.ERROR, var.MSG_INVALID_SPOTS_NUMBER_IN_HD)
            dlg.exec()
            # Restore GUI to last correct setting.
            main_ui.lineEdit_spots_number.setText(str(sensor_params.spots_number))
    except ValueError:
        if sensor_params.detection_field_mode == var.DETECTION_FIELD_MODE_HS:
            dlg = popup.CustomMessageBox(var.MESSAGE, var.MSG_INVALID_SPOTS_NUMBER_IN_HS)
            add_text_to_browser(var.ERROR, var.MSG_INVALID_SPOTS_NUMBER_IN_HS)
        else:
            dlg = popup.CustomMessageBox(var.MESSAGE, var.MSG_INVALID_SPOTS_NUMBER_IN_HD)
            add_text_to_browser(var.ERROR, var.MSG_INVALID_SPOTS_NUMBER_IN_HD)
        dlg.exec()
        add_text_to_browser(var.ERROR, 'Spots number must be an integer')
        # Restore GUI to last correct setting.
        main_ui.lineEdit_spots_number.setText(str(sensor_params.spots_number))
    finally:
        main_ui.lineEdit_spots_number.blockSignals(False)


from api.flatscan_utils import flatscan_measuring_head_error_parse, flatscan_rs485_error_parse
from PyQt6.QtCore import QTimer

flatscan_emergency = ""
flatscan_emergency_check_timer = None


def flatscan_emergency_handler(emergency_info):
    # print(emergency_info)
    global flatscan_emergency
    rs485_err_msg = color_text("rs485 error: ", colors.RED1) + flatscan_rs485_error_parse(
        emergency_info['RS485_error_code'])
    measuring_head_err_msg = color_text("measuring head error: ", colors.RED1) + flatscan_measuring_head_error_parse(
        emergency_info['measuring_head_error_code'])
    print_msg = rs485_err_msg + "\n" + measuring_head_err_msg
    # add_text_to_browser(var.ERROR, print_msg)
    flatscan_emergency = print_msg


def start_emergency_message_checker():
    global flatscan_emergency_check_timer
    flatscan_emergency_check_timer = QTimer()
    flatscan_emergency_check_timer.timeout.connect(emergency_message_checker)
    flatscan_emergency_check_timer.setInterval(100)
    flatscan_emergency_check_timer.start()


def emergency_message_checker():
    global flatscan_emergency
    if len(flatscan_emergency):
        dlg = popup.CustomMessageBox(var.ERROR, flatscan_emergency)
        add_text_to_browser(var.ERROR, flatscan_emergency)
        dlg.exec()
        flatscan_emergency = ""


def add_text_to_browser(text_type, text):
    formatted_str = text_brower_formatter(text_type, text)
    main_ui.textBrowser.append(formatted_str)


def text_brower_formatter(text_type, text):
    current_time = datetime.now()
    current_time = current_time.replace(microsecond=0)
    dateTimeStr = str(current_time)
    text_type_color = {var.ERROR: colors.RED1, var.INFO: colors.YELLOW1}
    return color_text(dateTimeStr, colors.GREEN) + ": (" + color_text(text_type,
                                                                      text_type_color[text_type]) + ") " + text


def color_text(text, color):
    return "<span style=\" color: {};\">{}</span>".format(hex_color(color), text)


def hex_color(color_rgb):
    return "#{0:02x}{1:02x}{2:02x}".format(*color_rgb)
