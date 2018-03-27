import logging
import requests
from sim_chat_lib.geotool_api import common
from sim_chat_lib.geotool_api import device_api

logger = logging.getLogger(__name__)

DEVICE_FIRMWARE_VERSION_API = "/api/device_firmware_version/"
FIRMWARE_API = "/api/firmware/"
DEVICE_FIRMWARE_BINARY_API = "/api/device_firmware_binary/"


def get_firmware_version(device_id):
    filter_str = "device=%s" % (device_id,)

    data = common.get_from_api(DEVICE_FIRMWARE_VERSION_API, filter_str)
    if data:
        try:
            if data.get("count", 0) == 1:
                return data["results"][0]["firmware"]["version"]
        except AttributeError as err:
            if len(data) == 1:
                return data[0]["firmware"]["version"]

    return None


def get_firmware_version_by_imei(imei):
    filter_str = "device__imei=%s" % (imei,)

    data = common.get_from_api(DEVICE_FIRMWARE_VERSION_API, filter_str)
    if data:
        try:
            if data.get("count", 0) == 1:
                return data["results"][0]["firmware"]["version"]
        except AttributeError as err:
            if len(data) == 1:
                return data[0]["firmware"]["version"]

    return None


def get_firmware(version):
    """
    Get firmware by version.
    :param version: version number to request
    :return: Dictionary with version and base64 encoding of file, or None if not found
    """
    filter_str = "version=%s" % (version,)
    data = common.get_from_api(FIRMWARE_API, filter_str, cacheable=True)
    if data:
        try:
            if data.get("count", 0) == 1:
                version = data["results"][0].get('version')
                firmware = data["results"][0].get('firmware')
                checksum = data["results"][0].get('checksum')
        except AttributeError as err:
            if len(data) == 1:
                version = data[0].get('version')
                firmware = data[0].get('firmware')
                checksum = data[0].get('checksum')

    if version and firmware:
        return {
            "version": version,
            "firmware": firmware,
            "checksum": checksum,
        }

    return None


def get_firmware_by_imei(imei):
    """
    Get firmware by device imei.
    :param version: version number to request
    :return: Dictionary with version and base64 encoding of file, or None if not found
    """
    version = get_firmware_version_by_imei(imei)
    return get_firmware(version)


def upload_firmware(version, file_name, file_content, check_sum, device_type):
    device_type_id = device_api.get_device_type_id_by_ident(device_type)
    if not device_type_id:
        logger.error("Unable to find the device type with ident: %s", device_type)
        return None
    data = {
        "version": version,
        "file_name":  file_name,
        "check_sum": check_sum,
        "firmware": file_content,
        "device_type": device_type_id,
    }
    response = common.post_to_api(FIRMWARE_API, data=data)

    return response


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
    print(
        timeit(
            'get_firmware(get_firmware_version_by_imei("77070407942500"))',
            "from __main__ import get_firmware, get_firmware_version_by_imei",
            number=1,
        )
    )
    print(
        timeit(
            'get_firmware(get_firmware_version_by_imei("77070407942500"))',
            "from __main__ import get_firmware, get_firmware_version_by_imei",
            number=1,
        )
    )
    print(get_firmware_version(20))
    print(get_firmware_version(9999))
    print(get_firmware(get_firmware_version(20)))
    print(get_firmware_version_by_imei("77070407942500"))

    print(get_firmware(get_firmware_version_by_imei("77070407942500")))
    print(get_firmware_by_imei("77070407942500"))
    print(get_firmware_by_imei("77070407942500"))
    print(upload_firmware("3", "3.zip", "dGVzdAo=", "nochecksum", 1))
