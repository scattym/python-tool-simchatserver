import logging
import requests
from sim_chat_lib.geotool_api import common
from sim_chat_lib.geotool_api import device_api

logger = logging.getLogger(__name__)

TRIP_LOG_API = "/api/trip_log/"


def get_latest_open_trip_by_device_id(device_id):
    filter_str = "device=%s&trip_end__isnull=True" % (device_id,)

    data = common.get_from_api(TRIP_LOG_API, filter_str, cacheable=False)

    if data:
        if data.get("count", 0) == 1:
            trip = data["results"][0]
            return trip


def add_trip_log_by_device_id(device_id, event_time, start_stop='start'):
    open_trip = get_latest_open_trip_by_device_id(device_id)
    if start_stop == 'start' and open_trip is not None:
        logger.error("Already an open trip for device %s", device_id)
    if start_stop == 'start' and open_trip is None:
        data = {
            "device": device_id,
            "trip_start": str(event_time),
            "trip_end": None,
        }
        result = common.post_to_api(common.TRIP_LOG_API, data)
        logger.debug("Update of trip log result: ", result)
        return result
    if start_stop == 'stop' and open_trip is not None:
        open_trip['trip_end'] = str(event_time)
        result = common.post_to_api(common.TRIP_LOG_API, open_trip, open_trip["id"])
        logger.debug("Update of trip log result: ", result)
        if result:
            return result
    if start_stop == 'stop' and open_trip is None:
        logger.error("Stop event but no open trip")
    return None


def add_trip_log_by_imei(device_imei, event_time, start_stop='start'):
    result = None
    device_pk = device_api.get_device_pk(device_imei)
    if not device_pk:
        logger.error("Unable to retrieve device information")
    else:
        return add_trip_log_by_device_id(device_pk, event_time, start_stop)


if __name__ == '__main__':
    log_level = 11 - 2

    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    common.set_api_host("localhost:8000")
    print(get_latest_open_trip_by_device_id(20))
    print(get_latest_open_trip_by_device_id(20))
    print(add_trip_log_by_imei("77070407942500", "2017-07-04 04:07:07Z", "start"))
    print(get_latest_open_trip_by_device_id(20))
    print(add_trip_log_by_device_id(20, "2017-07-04 04:07:07Z", "stop"))