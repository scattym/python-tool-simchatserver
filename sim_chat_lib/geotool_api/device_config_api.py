import requests
import logging
import traceback
from datetime import datetime
from sim_chat_lib.geotool_api import common
from sim_chat_lib.geotool_api import device_api

logger = logging.getLogger(__name__)


def get_device_config(ident):
    device_type = device_api.get_device_type_id_by_ident(ident)
