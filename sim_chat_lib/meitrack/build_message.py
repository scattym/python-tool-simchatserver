from sim_chat_lib.meitrack import command
from sim_chat_lib.meitrack.gprs_protocol import GPRS
from sim_chat_lib.meitrack.error import GPRSParameterError


def stc_request_photo_list(imei):
    com = command.stc_request_photo_list()
    gprs = GPRS()
    gprs.direction = '@@'
    gprs.data_identifier = 'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_request_location_message(imei):
    com = command.stc_request_location()
    gprs = GPRS()
    gprs.direction = '@@'
    gprs.data_identifier = 'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_set_heartbeat_interval(imei, minutes=0):
    com = command.stc_set_heartbeat(minutes)
    gprs = GPRS()
    gprs.direction = '@@'
    gprs.data_identifier = 'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_set_tracking_by_time_interval(imei, deci_seconds=0):
    com = command.stc_set_tracking_by_time_interval(deci_seconds)
    gprs = GPRS()
    gprs.direction = '@@'
    gprs.data_identifier = 'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# A13
def stc_set_cornering_angle(imei, angle=30):
    com = command.stc_set_cornering_angle(angle)
    gprs = GPRS()
    gprs.direction = '@@'
    gprs.data_identifier = 'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


# A14
def stc_set_tracking_by_distance(imei, meters=0):
    com = command.stc_set_tracking_by_distance(meters)
    gprs = GPRS()
    gprs.direction = '@@'
    gprs.data_identifier = 'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs

def stc_request_device_info(imei):
    com = command.stc_request_info()
    gprs = GPRS()
    gprs.direction = '@@'
    gprs.data_identifier = 'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


if __name__ == '__main__':
    test_gprs = stc_request_location_message("testimei")
    print(repr(test_gprs))
