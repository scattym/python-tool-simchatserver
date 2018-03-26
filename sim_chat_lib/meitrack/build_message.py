from sim_chat_lib.meitrack import command
from sim_chat_lib.meitrack.gprs_protocol import GPRS

def stc_request_location_message(imei):
    com = command.stc_request_location()
    gprs = GPRS()
    gprs.direction = '@@'
    gprs.data_identifier = 'X'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


if __name__ == '__main__':
    gprs = stc_request_location_message("testimei")
    print(repr(gprs))
