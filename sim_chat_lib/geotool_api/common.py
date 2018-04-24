import datetime
import traceback

import requests
import logging
import json
import simplejson
import os
import memcache
from cachetools import LRUCache

logger = logging.getLogger(__name__)

LOOKUP_METHOD_GOOGLE = "1"
LOOKUP_CACHE_DEPTH_IN_DAYS = 30

HEADERS = {
    'do': {
        'Authorization': 'Token 9554e04e2781705f45f54eaa8ba6a32a3b49294d',
    },
    'home': {
        'Authorization': 'Token 2e75eff12d410c60edce82b9f1a4742ef2fa9bb9',
    },
}

API_HOST = os.environ.get("GEO_API_HOST") or "webui.scattym.com:8000"
MEMGEOTOOL_API_CACHED_HOST = os.environ.get("MEMGEOTOOL_API_CACHED_HOST", "localhost")


DEVICE_API = "/api/device/"
REPORT_API = "/api/report/"
REPORT_GPS_API = "/api/reportgps/"
REPORT_GPS_RMC_API = "/api/reportgpsrmc/"
REPORT_GPS_VTG_API = "/api/reportgpsvtg/"
REPORT_GPS_GGA_API = "/api/reportgpsgga/"
OBDII_API = "/api/obdii/"
CELL_DATA_API = "/api/celldata/"
CELL_DATA_TO_LOCATION_API = "/api/celldata_to_location/"
DRIVER_API = "/api/driver/"
DRIVER_LOG_API = "/api/driver_log/"
TRIP_LOG_API = "/api/trip_log/"
DEVICE_UPDATE_API = "/api/deviceupdate/"
CAMERA_API = "/api/camera/"
MEITRACK_CONFIG_API = "/api/meitrack_config/"
EVENT_API = "/api/event/"

GEOTOOL_API_CACHE = None


GEOTOOL_API_CACHE_ENTRIES = {

}


class MemoryCache(object):
    def __init__(self):
        self.cache = LRUCache(maxsize=100)

    def set(self, key, data):
        logger.debug("Setting key %s to be %s", key, data)
        self.cache[key] = data

    def get(self, key):
        try:
            logger.debug("Asking for key %s", key)
            return self.cache.get(key)
        except KeyError as err:
            return None

    def get_stats(self):
        return self.cache


def check_cache_and_fallback():
    global GEOTOOL_API_CACHE
    stats = GEOTOOL_API_CACHE.get_stats()
    if not stats:
        GEOTOOL_API_CACHE = MEMORY_CACHE


def setup_cache():
    global GEOTOOL_API_CACHE
    cache_host = os.environ.get("MEMCACHE_HOST", "127.0.0.1:11211")
    GEOTOOL_API_CACHE = memcache.Client([cache_host])
    check_cache_and_fallback()


MEMORY_CACHE = MemoryCache()
setup_cache()


def add_cached_content(url, data):
    global GEOTOOL_API_CACHE, GEOTOOL_API_CACHE_ENTRIES
    if GEOTOOL_API_CACHE:
        GEOTOOL_API_CACHE.set(url, data)
    else:
        GEOTOOL_API_CACHE_ENTRIES[url] = data


def get_cached_content(url):
    global GEOTOOL_API_CACHE, GEOTOOL_API_CACHE_ENTRIES
    if GEOTOOL_API_CACHE:
        return GEOTOOL_API_CACHE.get(url)
    else:
        return GEOTOOL_API_CACHE_ENTRIES[url]


def get_cache_stats():
    global GEOTOOL_API_CACHE, GEOTOOL_API_CACHE_ENTRIES
    if GEOTOOL_API_CACHE:
        return "Using lru or memcache with stats: %s" % (GEOTOOL_API_CACHE.get_stats(),)
    else:
        return "Using memory cache. Contains %s" % (GEOTOOL_API_CACHE_ENTRIES,)


def set_api_host(host):
    global API_HOST
    API_HOST = host


def host_to_token_header(host):
    if "geotool.scattym.com" in host or "10.1.1.4" in host:
        return HEADERS['home']

    return HEADERS['do']


def post_to_api(endpoint, data, primary_key=None, cacheable=False, files=None):
    try:
        url = 'http://%s%s' % (API_HOST, endpoint)

        content_type="application/json"
        headers = host_to_token_header(API_HOST)
        if data:
            headers["Content-Type"] = "application/json"
        if data:
            post_data = json.dumps(data)
        else:
            post_data = data  # make sure we copy in the None

        if primary_key is not None:
            url = url + "%s/" % (primary_key,)
            response = requests.put(
                url,
                data=post_data,
                headers=headers,
                files=files,
            )
        else:
            response = requests.post(
                url,
                data=post_data,
                headers=headers,
                files=files,
            )
        logger.debug(response)
        logger.debug(response.text)
    except Exception as e:
        logger.error("Callout to geotool failed with error: %s", e)
        logger.debug(traceback.format_exc())
        raise e

    try:
        return_json = response.json()
    except simplejson.scanner.JSONDecodeError as err:
        logger.error("Could not parse json: %s", err)
        logger.error("Response was: %s", response.text)
        logger.error("Response code was: %s", response.status_code)
        return None

    return return_json


def get_from_api(endpoint, filter_str, cacheable=False):
    try:
        url = 'http://%s%s?%s' % (
            API_HOST,
            endpoint,
            filter_str
        )
        cached_result = get_cached_content(url)
        if cached_result:
            try:
                if cached_result["count"] == 0:
                    logger.error("Cached result count is 0")
                else:
                    return cached_result
            except ValueError as err:
                logger.error("Can't get count, returning cached data")
                return cached_result

        response = requests.get(
            url,
            headers=host_to_token_header(API_HOST)
        )
        logger.debug(response)
        logger.debug(response.text)
    except Exception as e:
        logger.error("Callout to geotool failed with error: %s", e)
        raise e
    if cacheable:
        try:
            if response.status_code != 200:
                logger.warn("Not caching errors, status code is %s", response.status_code)
            elif response.json()["count"] == 0:
                logger.warn("Not caching empty response")
            else:
                add_cached_content(url, response.json())
        except ValueError as err:
            logger.error("Unable to check count, adding to cache")
            add_cached_content(url, response.json())

    if response.status_code == 200:
        return response.json()

    return None
