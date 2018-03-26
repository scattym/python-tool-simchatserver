#!/usr/bin/env python
import logging

logger = logging.getLogger(__name__)
"""
payload $$<Data identifier><Data length>,<IMEI>,<Command type>,<Command><*Checksum>\r\n
"""

EVENT = {
    1: "Input 1 Active",
    2: "Input 2 Active",
    3: "Input 3 Active",
    4: "Input 4 Active",
    5: "Input 5 Active",
    9: "Input 1 Inactive",
    10: "Input 2 Inactive",
    11: "Input 3 Inactive",
    12: "Input 4 Inactive",
    13: "Input 5 Inactive",
    17: "Low Battery",
    18: "Low External Battery",
    19: "Speeding",
    20: "Enter Geo - fence",
    21: "Exit Geo - fence",
    22: "External Battery On",
    23: "External Battery Cut",
    24: "GPS Signal Lost",
    25: "GPS Signal Recovery",
    26: "Enter Sleep",
    27: "Exit Sleep",
    28: "GPS Antenna Cut",
    29: "Device Reboot",
    31: "Heartbeat /",
    32: "Heading Changed",
    33: "Track By Distance",
    34: "Reply Current",
    35: "Track By Time",
    36: "Tow",
    37: "iButton",
    39: "Picture",
    40: "Power Off",
    41: "Stop Moving",
    42: "Start Moving",
    44: "GSM Jammed",
    50: "Temperature High",
    51: "Temperature Low",
    52: "Fuel Fulled",
    53: "Fuel Empty",
    54: "Fuel Stolen",
    56: "Armed",
    57: "Disarmed",
    58: "Stealing",
    63: "GSM No Jamming",
    65: "Press Input 1(SOS) to Call",
    66: "Press Input 2 to Call",
    67: "Press Input 3 to Call",
    68: "Press Input 4 to Call",
    69: "Press Input 5 to Call",
    70: "Reject Incoming Call",
    71: "Get Location By Call",
    72: "Auto Answer Incoming Call",
    73: "Listen In(Voice Monitoring) ",
    79: "Fall",
    80: "Install",
    81: "Drop Off",
    129: "Harsh breaking",
    130: "Harsh Acceleration",
    133: "Idle Overtime",
    134: "Idle Recovery",
    139: "Maintenance Notice",
}


def event_id_to_name(event_id):
    try:
        return EVENT[event_id]
    except ValueError as err:
        return "Unknown event"


class Event(object):
    def __init__(self, payload=None):
        pass
