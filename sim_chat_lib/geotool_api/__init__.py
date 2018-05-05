
from sim_chat_lib.geotool_api import device_api, firmware_api, common, camera_api, trip_log_api, cell_api
from sim_chat_lib.geotool_api import session_key_api
from sim_chat_lib.geotool_api import device_key_api
from sim_chat_lib.geotool_api import event_log_api


def get_cache_stats():
    common.setup_cache()
    return common.get_cache_stats()


def get_firmware_version(device_id):
    return firmware_api.get_firmware_version(device_id)


def get_firmware(version):
    return firmware_api.get_firmware(version)


def get_firmware_version_by_imei(imei):
    return firmware_api.get_firmware_version_by_imei(imei)


def get_firmware_by_imei(imei):
    return firmware_api.get_firmware_by_imei(imei)


def get_session_key_by_imei(imei, uuid):
    device_pk = device_api.get_device_pk(imei)
    if device_pk:
        return device_api.get_session_key(device_pk, uuid)


def get_or_create_device_key(imei):
    device_pk = device_api.get_device_pk(imei)
    if device_pk:
        key = device_key_api.get_or_create_key(device_pk)
        return key


def add_event_log(imei, log_time, event_type, event_description):
    device_pk = device_api.get_device_pk(imei)
    if device_pk:
        return event_log_api.add_event(device_pk, log_time, event_type, event_description)


def add_trip_log(device_imei, event_time, start_stop='start'):
    device_pk = device_api.get_device_pk(device_imei)
    if device_pk:
        return trip_log_api.add_trip_log(device_pk, event_time, start_stop)


def add_sos_event(imei, log_time):
    device_pk = device_api.get_device_pk(imei)
    if device_pk:
        return event_log_api.add_sos_event(device_pk, log_time)


def add_camera_image(imei, camera_number, camera_time, image_data_jpg):
    device_pk = device_api.get_device_pk(imei)
    if device_pk:
        return camera_api.add_camera_image(device_pk, camera_number, camera_time, image_data_jpg)


def cell_update(imei, cell_id, location_area_code, mobile_country_code, mobile_network_code, ecio):
    device_pk = device_api.get_device_pk(imei)
    if device_pk:
        return cell_api.cell_update(device_pk, cell_id, location_area_code, mobile_country_code, mobile_network_code, ecio)
