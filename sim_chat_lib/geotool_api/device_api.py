import logging
import requests
from sim_chat_lib.geotool_api import common

logger = logging.getLogger(__name__)

DEVICE_API = "/api/device/"
DEVICE_TYPE_API = "/api/device_type/"


def get_device_pk(imei):
    filter_str = "imei=%s" % (imei,)
    response = common.get_from_api(DEVICE_API, filter_str, cacheable=True)

    if response:
        result_set = response
        try:
            if result_set.get("count", 0) == 1:
                return result_set["results"][0]["id"]
        except AttributeError as err:
            if len(result_set) == 1:
                return result_set[0]["id"]

    return None


def create_device(imei, **kwargs):
    device = {
        "imei": imei
    }
    for key, value in kwargs.items():
        device[key] = value

    result = common.post_to_api("%s" % (common.DEVICE_API,), device)

    if result and "id" in result:
        return result["id"]
    return None


def get_device_type_id_by_ident(ident):
    filter_str = "identifier=%s" % (ident,)
    response = common.get_from_api(DEVICE_TYPE_API, filter_str, cacheable=True)

    if response:
        result_set = response
        try:
            if result_set.get("count", 0) == 1:
                return result_set["results"][0]["id"]
        except AttributeError as err:
            if len(result_set) == 1:
                return result_set[0]["id"]
    return None


def device_update_by_long_lat(
    imei, longitude, latitude, true_track, ground_speed, altitude, dilution, age_gps_data, num_sats, timestamp, log_time
):
    location = "SRID=4326;POINT (%s %s)" % (longitude, latitude)
    device_update_by_location(
        imei, location, true_track, ground_speed, altitude, dilution, age_gps_data, num_sats, timestamp, log_time
    )


def device_update_by_location(
        imei, location, true_track, ground_speed, altitude, dilution, age_gps_data, num_sats, timestamp, log_time
):
    device_update = {
        "imei": imei,
        "location": location,  # "SRID=4326;POINT (151.07571 -33.636995)",
        "true_track": true_track,
        "ground_speed": ground_speed,
        "altitude": altitude,
        "dilution": dilution,
        "age_gps_data": age_gps_data,
        "num_sats": num_sats,
        "timestamp": str(timestamp),  # "2018-03-27T07:19:35+07:00",
        "log_time": str(log_time),  # "2018-03-27T07:19:35.619512+07:00"
    }

    result = common.post_to_api("%s" % (common.DEVICE_UPDATE_API,), device_update)

    return result


def cell_update(
        imei, battery_level, battery_voltage, mcc, mnc, lac, cell_id, rx_level, timestamp, log_time
):
    call_update_dict = {
        'battery_level': battery_level,
        'battery_voltage': battery_voltage,
        'log_time': str(log_time),  # "2018-03-27T07:19:35.619512+07:00"
        'cell_id': cell_id,
        'location_area_code': lac,
        'mobile_country_code': mcc,
        'mobile_network_code': mnc,
        'rx_level': rx_level,
        "imei": imei,
        "timestamp": str(timestamp),  # "2018-03-27T07:19:35+07:00",
    }

    result = common.post_to_api("%s" % (common.CELL_DATA_API,), call_update_dict)

    return result


if __name__ == '__main__':
    from timeit import timeit
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
    print(get_device_type_id_by_ident("simcom5300"))
    print(get_device_pk("77070407942500"))
    print(create_device("77070407942501"))
    print(create_device("770704079425", name="Another API test"))
    # report_pk = create_report(10)
    # report_gps_pk = create_report_gps(report_pk)
    # 031924.0, A, 3348.948974, S, 15112.009167, E, 0.0, 0.0, 141017,, ,
    # 151.200 -33.816
    # location = coord_dec_to_point_field(151.200, -33.816)
    # location = coord_nmea_to_point_field(15112.009167, 'E', 3348.948974, 'S')