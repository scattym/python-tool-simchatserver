
from nmea_proxy_lib.geolocation_api.common import entry_to_cell_tower
OPENCELL_MAP = {
    "cid": "cell_id",
    "lac": "location_area_code",
    "mcc": "mobile_country_code",
    "mnc": "mobile_network_code",
    "signal": "rx_level",
    "tA": "timing_advance",
}

def cell_list_to_opencell_list(cell_list):
    return_list = []
    for entry in cell_list:
        opencell_tower = entry_to_cell_tower(entry, OPENCELL_MAP)
        return_list.append(opencell_tower)
    return return_list