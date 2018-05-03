import requests
import logging
import traceback
from datetime import datetime
from sim_chat_lib.geotool_api import common
from sim_chat_lib.geotool_api import device_api, driver_api
from sim_chat_lib.license import cardreader

logger = logging.getLogger(__name__)


def get_driver_by_license(license_number):
    try:
        url = 'http://%s%s?license_number=%s' % (common.API_HOST, common.DRIVER_API, license_number)

        response = requests.get(
            url,
            headers=common.host_to_token_header(common.API_HOST)
        )
        logger.debug(response)
        logger.debug(response.text)
    except Exception as e:
        logger.error("Callout to geotool failed with error: %s", e)
        raise e

    if response.status_code == 404:
        return None

    result_set = response.json()
    try:
        if result_set.get("count", 0) == 1:
            return result_set["results"][0]
    except AttributeError as err:
        if len(result_set) == 1:
            return result_set[0]

    return None


def get_driver_by_id_number(id_number):
    try:
        url = 'http://%s%s?id_number=%s' % (common.API_HOST, common.DRIVER_API, id_number)

        response = requests.get(
            url,
            headers=common.host_to_token_header(common.API_HOST)
        )
        logger.debug(response)
        logger.debug(response.text)
    except Exception as e:
        logger.error("Callout to geotool failed with error: %s", e)
        raise e

    if response.status_code == 404:
        return None

    result_set = response.json()
    try:
        if result_set.get("count", 0) == 1:
            return result_set["results"][0]
    except AttributeError as err:
        if len(result_set) == 1:
            return result_set[0]

    return None


def add_driver(pk, license_number, name, id_number, date_of_birth, expiration_date, phone_number=None):
    try:
        if date_of_birth and len(date_of_birth) == 8:
            date_of_birth = datetime.strptime(date_of_birth, "%Y%m%d").strftime("%Y-%m-%d")
        else:
            date_of_birth = None
        if expiration_date == '9999':
            expiration_date = '209912'
        if expiration_date:
            expiration_date = datetime.strptime(expiration_date, "%Y%m").strftime("%Y-%m-%d")
        data = {
            "pk": pk,
            "license_number": license_number,
            "name": name,
            "id_number": id_number,
            "date_of_birth": date_of_birth,
            "expiration_date": expiration_date,
            "phone_number": phone_number,
        }
        result = common.post_to_api(common.DRIVER_API, data)
        logger.debug("Add driver result was: ", result)
        if result:
            return result
    except Exception as err:
        logger.error("Exception in add driver: %s", err)
        logger.error(
            "Payload: pk: %s license_number: %s name: %s id_number: %s date_of_birth: %s "
            "expiration_date: %s phone_number: %s",
            pk,
            license_number,
            name,
            id_number,
            date_of_birth,
            expiration_date,
            phone_number
        )
        logger.error(traceback.format_exc())
    return None


def add_driver_log_by_keys(device_pk, driver_pk):
    data = {
        'device': device_pk,
        'driver': driver_pk,
    }
    result = common.post_to_api(common.DRIVER_LOG_API, data)
    logger.debug("Add driver result was: ", result)
    if result:
        return result
    return None


def add_driver_log(device_imei, license_number=None, id_number=None):
    result = None
    device_pk = device_api.get_device_pk(device_imei)
    if not device_pk:
        logger.error("Unable to retrieve device information")
    else:
        driver = None
        if license_number:
            driver = get_driver_by_license(license_number=license_number)
        elif id_number:
            driver = get_driver_by_license(id_number=id_number)
        else:
            logger.error(
                "Unable to lookup driver: imei: %s, license_number: %s, id_number: %s",
                device_imei, license_number, id_number
            )

    if device_pk and driver and driver.get('pk'):
        result = add_driver_log_by_keys(device_pk, driver.get('pk'))
        logger.debug("Add driver log result was: %s", result)
    else:
        logger.error("Failed to lookup one of the primary keys")

    return result


def add_driver_log_by_payload(imei, payload):
    drivers_license = cardreader.License(payload)
    logger.debug("License is %s", drivers_license)
    driver = driver_api.add_driver(
        None,
        drivers_license.get_field('license_number'),
        drivers_license.get_field('name'),
        drivers_license.get_field('id_number'),
        drivers_license.get_field('date_of_birth'),
        drivers_license.get_expiration_date(),
    )

    if driver :
        result = driver_api.add_driver_log(
            imei,
            license_number=driver.get('license_number'),
            id_number=driver.get('id_number')
        )


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
    print(add_driver(None, '1', 'someone', '111222', '19770704', '209912', '+61402144176'))
    print(add_driver(None, '1', 'someone', '111222', '19770704', '9999', '+61402144176'))
    print(add_driver(None, '1', None, None, None, None, None))
    print(add_driver(2, None, None, None, None, None, None))
    print(add_driver(None, None, None, None, None, None, None))
    print(get_driver_by_id_number('111222'))
    print(get_driver_by_license('1'))