from sim_chat_lib.meitrack import command
from sim_chat_lib.meitrack.gprs_protocol import GPRS
from sim_chat_lib.meitrack.error import GPRSParameterError


def stc_request_device_info(imei):
    com = command.stc_request_info()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_request_get_file(imei, file_name, payload_start_index=0):
    com = command.stc_request_file_download(file_name, payload_start_index)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'b'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_request_location_message(imei):
    com = command.stc_request_location()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'c'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_request_photo_list(imei):
    com = command.stc_request_photo_list()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'd'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_request_take_photo(imei, camera_number, file_name):
    com = command.stc_request_take_photo(camera_number, file_name=file_name)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'e'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# A13
def stc_set_cornering_angle(imei, angle=30):
    com = command.stc_set_cornering_angle(angle)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'f'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# B07
def stc_set_speeding_alert(imei, speed_kmh=0, disabled=True):
    com = command.stc_set_speeding_alert(speed_kmh, disabled)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'g'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# B14
def stc_set_idle_alert_time(imei, consecutive_speed_time_secs=0, speed_kmh=0, alert_time_secs=0):
    com = command.stc_set_idle_alert_time(consecutive_speed_time_secs, speed_kmh, alert_time_secs)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'h'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs

# B15
def stc_set_fatigue_driving_alert_time(imei, consecutive_driving_time_mins=0, alert_time_secs=0, acc_off_time_mins=0):
    com = command.stc_set_fatigue_driving_alert(consecutive_driving_time_mins, alert_time_secs, acc_off_time_mins)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'i'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# C50
def stc_set_driver_license_type(imei, license_type_str=None):
    com = command.stc_set_driver_license_type(license_type_str)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'j'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# C52
def stc_set_driver_license_validity_time(imei, validity_time):
    com = command.stc_set_driver_license_validity_time(validity_time)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'k'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_set_heartbeat_interval(imei, minutes=0):
    com = command.stc_set_heartbeat(minutes)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'l'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# A14
def stc_set_tracking_by_distance(imei, meters=0):
    com = command.stc_set_tracking_by_distance(meters)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'm'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# B36
def stc_set_time_zone(imei, minutes=0):
    com = command.stc_set_time_zone(minutes)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'n'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_set_tracking_by_time_interval(imei, deci_seconds=0):
    com = command.stc_set_tracking_by_time_interval(deci_seconds)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'o'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


if __name__ == '__main__':
    test_gprs = stc_request_location_message(b"testimei")
    print(test_gprs.as_bytes())
    print(stc_request_device_info(b"0407").as_bytes())
