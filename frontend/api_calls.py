flatscan = None
renderer = None


def set_renderer(r):
    global renderer
    renderer = r


def set_flatscan(f):
    global flatscan
    flatscan = f

def close_flatscan():
    global flatscan
    flatscan.close()


def get_parameter(sensor_params):
    params = flatscan.get_parameters()
    # Store params to sensor_params.
    sensor_params.angle_first = params['angle_first'] / 100
    sensor_params.angle_last = params['angle_last'] / 100
    sensor_params.detection_field_mode = params['detection_field_mode']
    sensor_params.spots_number = params['num_spots']
    sensor_params.optimization = params['sensitivity']
    sensor_params.information_in_mdi = params['mdi_info']
    sensor_params.averaging = params['averaging']
    sensor_params.enable_can = params['can_and_frame_counter']
    sensor_params.enable_ctn = params['temperature']  # CTN: temperature
    sensor_params.enable_facet = params['facet_number_field']
    return "Get parameters success"


def set_parameter(sensor_params):
    # Pass the parameters of sensor_params to backend
    params = dict()
    params['temperature'] = int(sensor_params.enable_ctn)
    params['mdi_info'] = int(sensor_params.information_in_mdi)
    params['detection_field_mode'] = int(sensor_params.detection_field_mode)
    params['sensitivity'] = int(sensor_params.optimization)
    params['num_spots'] = int(sensor_params.spots_number)
    params['angle_first'] = int(sensor_params.angle_first * 100)
    params['angle_last'] = int(sensor_params.angle_last * 100)
    params['can_and_frame_counter'] = int(sensor_params.enable_can)
    params['facet_number_field'] = int(sensor_params.enable_facet)
    params['averaging'] = int(sensor_params.averaging)
    renderer.set_new_frame_context(angle_first=sensor_params.angle_first, angle_last=sensor_params.angle_last)
    return str(flatscan.set_parameters(**params))


def get_mdi():
    if flatscan is None:
        return {'distances': []}
    return flatscan.get_mdi()


def get_identity():
    return flatscan.get_identity()

def reset_mdi_counter():
    return flatscan.reset_mdi_counter()


def save_params_to_file(file):
    msg = flatscan.save_parameters(file)
    return 'Save Params To File API called: ' + str(msg)


def read_params_from_file(file):
    msg = flatscan.load_parameters(file)
    return 'Read Params From FIle API called: ' + str(msg)


def export_log(file):
    flatscan.export_log(file)
    return 'Export Log API called'

# Store params
