import logging
import requests
from sim_chat_lib.geotool_api import common

logger = logging.getLogger(__name__)

EVENT_TYPE_EMERGENCY = '0'
EVENT_TYPE_WARNING = '1'
EVENT_TYPE_INFORMATION = '2'


def add_event(device_pk, timestamp, event_type, event_description, log_time):
    data = {
        "device": device_pk,
        "timestamp":  str(timestamp),
        "event_type": event_type,
        "event_description": event_description,
        "log_time": str(log_time),
    }
    response = common.post_to_api(common.EVENT_API, data=data)

    return response


def add_sos_event(device_pk, timestamp, log_time):
    return add_event(device_pk, timestamp, EVENT_TYPE_EMERGENCY, "SOS button pressed", log_time)


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
    test_response = add_event(20, "2018-03-03 12:12:12Z", EVENT_TYPE_INFORMATION, "A message")
    print(test_response)
    test_response = add_sos_event(20, "2018-03-03 12:12:12Z", "2018-03-03 12:12:12Z")
    print(test_response)
