import requests
import logging
import traceback
from datetime import datetime
from sim_chat_lib.geotool_api import common
from sim_chat_lib.geotool_api import device_api

logger = logging.getLogger(__name__)


def get_device_config(device_pk):
    filter_str = "device=%s" % (device_pk,)

    filter_str = "device__isnull=True"
    data = common.get_from_api(common.MEITRACK_CONFIG_API, filter_str)
    if data:
        if data.get("count", 0) == 1:
            return data["results"][0]

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
    config = get_device_config(20)
    print(config)
