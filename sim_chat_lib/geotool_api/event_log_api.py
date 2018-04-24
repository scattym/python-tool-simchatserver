import logging
import requests
from sim_chat_lib.geotool_api import common

logger = logging.getLogger(__name__)

EVENT_API = "/api/event_log/"

EVENT_TYPE_EMERGENCY = '0'
EVENT_TYPE_WARNING = '1'
EVENT_TYPE_INFORMATION = '2'


def add_event(device_pk, log_time, event_type, event_description):
    data = {
        "device": device_pk,
        "log_time":  str(log_time),
        "event_type": event_type,
        "event_description": event_description,
    }
    response = common.post_to_api(EVENT_API, data=data)

    return response


def add_ignition_event(device_pk, log_time, start_stop):
    if start_stop.lower() == "start":
        return add_event(device_pk, log_time, EVENT_TYPE_INFORMATION, "Engine start")
    if start_stop.lower() == "stop":
        return add_event(device_pk, log_time, EVENT_TYPE_INFORMATION, "Engine stop")


def add_sos_event(device_pk, log_time):
    return add_event(device_pk, log_time, EVENT_TYPE_EMERGENCY, "SOS button pressed")


"""
{
    "device": null,
    "log_time": null,
    "event_type": null,
    "event_description": "",
    "acknowledged_time": null,
    "acknowledged_flag": false
}
"""

if __name__ == '__main__':
    log_level = 11 - 2

    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    common.set_api_host("localhost:8000")
    response = add_event(20, "2018-03-03 12:12:12Z", EVENT_TYPE_INFORMATION, "A message")
    print(response)
    response = add_ignition_event(20, "2018-03-03 12:12:12Z", "start")
    print(response)
    response = add_ignition_event(20, "2018-03-03 12:12:12Z", "stop")
    print(response)
    response = add_sos_event(20, "2018-03-03 12:12:12Z")
    print(response)