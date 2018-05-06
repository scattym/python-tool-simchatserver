import requests
import logging
from datetime import datetime
from sim_chat_lib.geotool_api import common

logger = logging.getLogger(__name__)

def get_cell_id(lac, mcc, mnc, psc):
    try:
        url = 'http://%s/device/locate_cell/%s/%s/%s/%s' % (
            common.API_HOST,
            lac,
            mcc,
            mnc,
            psc
        )
        response = requests.get(
            url,
            headers=common.host_to_token_header(common.API_HOST),
        )
        logger.debug(response)
        logger.debug(response.text)
    except Exception as e:
        logger.error("Callout to geotool failed with error: %s", e)
        return None

    if response.status_code == 404:
        return None

    result_set = response.json()

    return result_set.get("cell_id", None)


def get_location_from_cell(cell_id, lac, mcc, mnc, rx_level, lookup_method=common.LOOKUP_METHOD_GOOGLE):
    start_date = datetime.datetime.now() + datetime.timedelta(days=-common.LOOKUP_CACHE_DEPTH_IN_DAYS)

    if None in [cell_id, lac, mcc, mnc, rx_level]:
        return None
    try:
        query_string = (
            "cell_id=%s&location_area_code=%s&mobile_country_code=%s&"
            "mobile_network_code=%s&rx_level=%s&log_time__gt=%s&page_size=1" % (
                cell_id,
                lac,
                mcc,
                mnc,
                rx_level,
                start_date,
            )
        )
        if lookup_method:
            query_string = "%s&lookup_method=%s" % (query_string, lookup_method,)

        url = 'http://%s%s?%s' % (
            common.API_HOST,
            common.CELL_DATA_TO_LOCATION_API,
            query_string,
        )
        print(url)
        response = requests.get(
            url,
            headers=common.host_to_token_header(common.API_HOST),
        )
        print(response)
        logger.debug(response)
        logger.debug(response.text)
    except Exception as e:
        logger.error("Callout to geotool failed with error: %s", e)
        return None

    if response.status_code == 404:
        return None

    result_set = response.json()
    if result_set.get("count", 0):
        return result_set["results"][0]

    return result_set


def cell_update(device_pk, log_time, cell_id, location_area_code, mobile_country_code, mobile_network_code, ecio):
    update_dict = {
        "log_time": str(log_time),
        "device": device_pk,
        "cell_id": cell_id,
        "location_area_code": location_area_code,
        "mobile_country_code": mobile_country_code,
        "mobile_network_code": mobile_network_code,
        "ecio": ecio,
    }

    result = common.post_to_api(common.CELL_DATA_SIMPLE_API, update_dict)
    return result


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
    print(get_cell_id(338, 505, 1, 278))
    print(get_cell_id(338, 505, 1, 0))
    print(get_location_from_cell(14302219, 338, 505, 1, -82))
