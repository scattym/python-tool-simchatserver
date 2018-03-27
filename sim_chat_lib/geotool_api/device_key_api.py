from Crypto.PublicKey import RSA
import logging
from sim_chat_lib.geotool_api import common

logger = logging.getLogger(__name__)

DEVICE_KEY_API = "/api/device_key/"


def store_device_key(device_pk, device_key):
    """

    :param device_pk: primary key of device
    :param device_key: rsa key to be stored
    :return: geotool api response as json
    """
    data = {
        "device": device_pk,
        "device_key":  device_key.exportKey('PEM', passphrase='OGJkZDllZGUzNjU1MTI0MzAzYTI2OTczOGMyODhlMmEgIC0K'),
    }
    response = common.post_to_api(DEVICE_KEY_API, data=data)

    return response


def get_device_key(device_pk):
    filter_str = "device=%s" % (device_pk,)
    logger.debug("Filter is %s", filter_str)

    data = common.get_from_api(DEVICE_KEY_API, filter_str, cacheable=True)
    logger.debug("device key response %s", data)
    if data:
        if data.get("count", 0) == 1:
            pem = data["results"][0]["device_key"]
            key = RSA.importKey(pem, passphrase='OGJkZDllZGUzNjU1MTI0MzAzYTI2OTczOGMyODhlMmEgIC0K')
            return key
        else:
            if data.get("count", 0) > 1:
                logger.error("Got more than one key back for the device.")

    return None


def get_or_create_key(device_pk):
    key = get_device_key(device_pk)
    if not key:
        new_key = generate_new_key()
        logger.debug("New key is %s", new_key)
        result = store_device_key(device_pk, new_key)
        if result:
            key = new_key

    return key


def generate_new_key(bits=1024):
    key = RSA.generate(bits)
    return key


if __name__ == '__main__':
    log_level = 11 - 11

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    common.set_api_host("localhost:8000")
    test_key = get_or_create_key(22)
    print(test_key)
    print(get_device_key(22))
