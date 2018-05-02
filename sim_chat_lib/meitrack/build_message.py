from sim_chat_lib.meitrack import command
from sim_chat_lib.meitrack.gprs_protocol import GPRS
from sim_chat_lib.meitrack.error import GPRSParameterError


def stc_request_get_file(imei, file_name, payload_start_index=0):
    com = command.stc_request_file_download(file_name, payload_start_index)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_request_take_photo(imei, camera_number, file_name):
    com = command.stc_request_take_photo(camera_number, file_name=file_name)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_request_photo_list(imei):
    com = command.stc_request_photo_list()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_request_location_message(imei):
    com = command.stc_request_location()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_set_heartbeat_interval(imei, minutes=0):
    com = command.stc_set_heartbeat(minutes)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_set_tracking_by_time_interval(imei, deci_seconds=0):
    com = command.stc_set_tracking_by_time_interval(deci_seconds)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# A13
def stc_set_cornering_angle(imei, angle=30):
    com = command.stc_set_cornering_angle(angle)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# A14
def stc_set_tracking_by_distance(imei, meters=0):
    com = command.stc_set_tracking_by_distance(meters)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# B36
def stc_set_time_zone(imei, minutes=0):
    com = command.stc_set_time_zone(minutes)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# C50
def stc_set_driver_license_type(imei, license_type_str=None):
    com = command.stc_set_driver_license_type(license_type_str)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_request_device_info(imei):
    com = command.stc_request_info()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


if __name__ == '__main__':
    test_gprs = stc_request_location_message(b"testimei")
    print(test_gprs.as_bytes())
    print(stc_request_device_info(b"0407").as_bytes())
