#!/usr/bin/env python
import requests
import logging
import json
import copy
from nmea_proxy_lib.geolocation_api.common import entry_to_cell_tower, LOOKUP_CELL_ID
from nmea_proxy_lib import geo_tool_api
from pprint import pprint

logger = logging.getLogger(__name__)

API_KEY = 'AIzaSyCuwOzYCRCXBCqsXSLKwijLTxQQfjABGLQ'
GOOGLE_MAP = {
    "cellId": "cell_id",
    "locationAreaCode": "location_area_code",
    "mobileCountryCode": "mobile_country_code",
    "mobileNetworkCode": "mobile_network_code",
    "signalStrength": "rx_level",
}


def callout_to_google(entry):
    google_json = cell_data_to_gapi(entry)
    print("############################### %s" % google_json)
    if not is_valid_google_request(google_json):
        return None

    url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_KEY
    # pprint(google_json)
    logger.debug(google_json)
    r = requests.post(
        url,
        json=google_json,
    )
    google_response = json.loads(r.text)
    if "location" in google_response:
        if "lat" in google_response["location"]:
            entry["latitude"] = google_response["location"]["lat"]
        if "lng" in google_response["location"]:
            entry["longitude"] = google_response["location"]["lng"]
    if "accuracy" in google_response:
        entry["accuracy"] = google_response["accuracy"]


def cell_list_to_google_cell_list(cell_list):
    return_list = []
    mnc = None
    lac = None
    mcc = None
    for entry in cell_list:
        if "cell_id" in entry:
            google_cell = entry_to_cell_tower(entry, GOOGLE_MAP)
            if "cellId" in google_cell:
                if "mobileCountryCode" in google_cell:
                    mcc = google_cell["mobileCountryCode"]
                if "mobileNetworkCode" in google_cell:
                    mnc = google_cell["mobileNetworkCode"]
                if "locationAreaCode" in google_cell:
                    lac = google_cell["locationAreaCode"]
                return_list.append(google_cell)
        else:
            if LOOKUP_CELL_ID:
                gcell = entry_to_cell_tower_fuzzy(entry, lac, mcc, mnc)
                if gcell and gcell["signalStrength"] != -119:
                    return_list.append(gcell)
    return return_list


def cell_data_to_gapi(entry):
    request = {
        "homeMobileCountryCode": 505,
        "homeMobileNetworkCode": 1,
        "considerIp": "false",
    }

    if "MODE" in entry:
        if entry["MODE"] == "GSM":
            request["radioType"] = "gsm"
        if entry["MODE"] == "WCDMA":
            request["radioType"] = "wcdma"
        if entry["MODE"] == "LTE":
            request["radioType"] = "lte"
        if entry["MODE"] == "CDMA":
            request["radioType"] = "cdma"
    if "cops" in entry:
        if "telstra" in entry["cops"].lower():
            request["carrier"] = "telstra"
        if "optus" in entry["cops"].lower():
            request["carrier"] = "optus"

    if "cell_list" in entry and len(entry["cell_list"]) > 0:
        request["cellTowers"] = cell_list_to_google_cell_list(
            entry["cell_list"]
        )
    else:
        request["cellTowers"] = [entry_to_cell_tower(entry, GOOGLE_MAP)]
    logger.debug("The google api request is: %s" % (request))
    return request


def entry_to_cell_tower_fuzzy(entry, lac, mcc, mnc):
    entry_copy = copy.deepcopy(entry)
    cell_id = geo_tool_api.get_cell_id(
        lac, mcc, mnc, entry["primary_scrambling_code"]
    )
    if cell_id:
        entry_copy["location_area_code"] = lac
        entry_copy["mobile_country_code"] = mcc
        entry_copy["mobile_network_code"] = mnc
        entry_copy["cell_id"] = cell_id
        return entry_to_cell_tower(entry_copy, GOOGLE_MAP)


def is_valid_google_request(google_json):
    if "cellTowers" not in google_json:
        return False

    for entry in google_json["cellTowers"]:
        # return true if we find a valid record
        if None not in [
            entry.get("cellId"),
            entry.get("locationAreaCode"),
            entry.get("mobileCountryCode"),
            entry.get("mobileNetworkCode"),
            entry.get("signalStrength"),
        ]:
            return True
    # No valid record found
    return False
