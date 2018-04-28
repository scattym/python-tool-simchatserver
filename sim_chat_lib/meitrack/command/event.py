"""
Library for managing event codes and mappings to text
"""
import logging
from functools import singledispatch

logger = logging.getLogger(__name__)

EVENT_MAP = {
    1: "SOS Pressed ",
    2: "Input 2 Active ",
    3: "Input 3 Active ",
    4: "Input 4 Active ",
    5: "Input 5 Active ",
    9: "Input 1 Inactive ",
    10: "Input 2 Inactive ",
    11: "Input 3 Inactive ",
    12: "Input 4 Inactive ",
    13: "Input 5 Inactive ",
    17: "Low Battery ",
    18: "Low External Battery ",
    19: "Speeding ",
    20: "Enter Geo-fence ",
    21: "Exit Geo-fence ",
    22: "External Battery On ",
    23: "External Battery Cut ",
    24: "GPS Signal Lost ",
    25: "GPS Signal Recovery ",
    26: "Enter Sleep",
    27: "Exit Sleep",
    28: "GPS Antenna Cut",
    29: "Device Reboot",
    31: "Heartbeat",
    32: "Cornering",
    33: "Track By Distance",
    34: "Reply Current (Passive)",
    35: "Track By Time Interval",
    36: "Tow",
    37: "RFID",
    39: "Photo",
    40: "Power Off",
    41: "Stop Moving",
    42: "Start Moving",
    44: "GSM Jamming",
    50: "Temperature High",
    51: "Temperature Low",
    52: "Full Fuel",
    53: "Low Fuel",
    54: "Fuel Theft",
    56: "Armed",
    57: "Disarmed",
    58: "Vehicle Theft",
    63: "No GSM Jamming",
    65: "Press Input 1 (SOS) to Call",
    66: "Press Input 2 to Call",
    67: "Press Input 3 to Call",
    68: "Press Input 4 to Call",
    69: "Press Input 5 to Call",
    70: "Reject Incoming Call",
    71: "Get Location by Call",
    72: "Auto Answer Incoming Call",
    73: "Listen-in (Voice Monitoring)",
    79: "Fall",
    80: "Install",
    81: "Drop Off",
    139: "Maintenance Notice",
}


@singledispatch
def event_to_name(event_code: int) -> str:
    return_str = EVENT_MAP.get(event_code)
    if not return_str:
        logger.error("Unable to lookup event code %s", event_code)

    return return_str


@event_to_name.register(str)
def _(event_code: str) -> str:
    try:
        lookup_value = int(event_code)
        return event_to_name(lookup_value)
    except ValueError as err:
        logger.error("Unable to process integer from string {}".format(event_code))


@event_to_name.register(bytes)
def _(event_code: bytes) -> str:
    try:
        lookup_value = int(event_code.decode())
        return event_to_name(lookup_value)
    except ValueError as err:
        logger.error("Unable to process integer from bytes {}".format(event_code))


if __name__ == "__main__":
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

    for key in EVENT_MAP:
        print(event_to_name(key))
        print(event_to_name(str(key).encode()))
        print(event_to_name(str(key)))
    print(event_to_name(None))
