
from sim_chat_lib.geotool_api import device_api, firmware_api, common
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


def add_ignition_event(imei, log_time, start_stop):
    device_pk = device_api.get_device_pk(imei)
    if device_pk:
        return event_log_api.add_ignition_event(device_pk, log_time, start_stop)


def add_sos_event(imei, log_time):
    device_pk = device_api.get_device_pk(imei)
    if device_pk:
        return event_log_api.add_sos_event(device_pk, log_time)
