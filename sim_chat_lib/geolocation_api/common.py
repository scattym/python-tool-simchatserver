import logging

logger = logging.getLogger(__name__)

LOOKUP_CELL_ID = False

#     "cellId": "cell_id",
#    "locationAreaCode": "location_area_code",
#    "mobileCountryCode": "mobile_country_code",
#    "mobileNetworkCode": "mobile_network_code",
#    "signalStrength": "rx_level",
def entry_to_cell_tower(entry, api_map):
    logger.debug(entry)
    cell = {}
    if "rx_level" in entry and isinstance(entry["rx_level"], basestring):
        if "dbm" in entry["rx_level"] or "dBm" in ["rx_level"]:
            entry["rx_level"] = entry["rx_level"].replace(
                "dbm", "").replace("dBm", "")
    for key in api_map:
        if api_map[key] in entry:
            if isinstance(entry[api_map[key]], basestring) and (
                    "dBm" in entry[api_map[key]] or "dbm" in entry[api_map[key]]):
                entry[api_map[key]] = entry[api_map[key]].replace(
                    "dBm", "").replace("dbm", "")
            cell[key] = int(entry[api_map[key]])
    return cell