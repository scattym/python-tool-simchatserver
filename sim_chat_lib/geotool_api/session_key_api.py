import logging
import base64
from sim_chat_lib.geotool_api import common

logger = logging.getLogger(__name__)

SESSION_KEY_API = "/api/session_key/"


def store_session_key(device_pk, session_key):
    data = {
        "device": device_pk,
        "session_key":  base64.b64encode(session_key),
    }
    response = common.post_to_api(SESSION_KEY_API, data=data)

    return response


def get_session_key(device_pk, uuid):
    filter_str = "id=%s&device=%s" % (uuid, device_pk)

    data = common.get_from_api(SESSION_KEY_API, filter_str, cacheable=True)
    if data:
        try:
            if data.get("count", 0) == 1:
                base64_session_key = data["results"][0]["session_key"]
                return base64.b64decode(base64_session_key)
        except AttributeError as err:
            if len(data) == 1:
                base64_session_key = data[0]["session_key"]
                return base64.b64decode(base64_session_key)

    return None


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
    key = store_session_key(20, "lkjlkj")
    print(key)
    print(get_session_key(20, key["id"]))
