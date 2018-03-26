#!/usr/bin/env python
import logging

import sys
from sim_chat_lib.meitrack import event
from sim_chat_lib.meitrack.command.command_AAA import TrackerCommand
from sim_chat_lib.meitrack.command.common import Command

logger = logging.getLogger(__name__)

COMMAND_LIST = {
    "A10": {"name": "Real-Time Location Query", "class": None},
    "A11": {"name": "Setting a Heartbeat Packet Reporting Interval", "class": None},
    "A12": {"name": "Tracking by Time Interval", "class": None},
    "A13": {"name": "Setting the Cornering Report Function", "class": None},
    "A14": {"name": "Tracking by Distance", "class": None},
    "A15": {"name": "Setting the Parking Scheduled Tracking Function", "class": None},
    "A16": {"name": "Enabling the Parking Scheduled Tracking Function", "class": None},
    "A21": {"name": "Setting GPRS Parameters", "class": None},
    "A22": {"name": "Setting the DNS Server IP Address", "class": None},
    "A23": {"name": "Setting the Standby GPRS Server", "class": None},
    "A70": {"name": "Reading All Authorized Phone Numbers", "class": None},
    "A71": {"name": "Setting Authorized Phone Numbers", "class": None},
    "A73": {"name": "Setting the Smart Sleep Mode", "class": None},
    "AAA": {"name": "Automatic Event Report", "class": TrackerCommand},
    "AFF": {"name": "Deleting a GPRS Event in the Buffer", "class": None},
    "B05": {"name": "Setting a Geo-Fence", "class": None},
    "B06": {"name": "Deleting a Geo-Fence", "class": None},
    "B07": {"name": "Setting the Speeding Alarm Function", "class": None},
    "B08": {"name": "Setting the Towing Alarm Function", "class": None},
    "B21": {"name": "Setting the Anti-Theft Function", "class": None},
    "B34": {"name": "Setting a Log Interval", "class": None},
    "B35": {"name": "Setting the SMS Time Zone", "class": None},
    "B36": {"name": "Setting the GPRS Time Zone", "class": None},
    "B60": {"name": "Checking the Engine First to Determine Tracker Running Status", "class": None},
    "B99": {"name": "Setting Event Authorization", "class": None},
    "C01": {"name": "Controlling Output Status", "class": None},
    "C02": {"name": "Notifying the Tracker of Sending an SMS", "class": None},
    "C03": {"name": "Setting a GPRS Event Transmission Mode", "class": None},
    "C08": {"name": "Setting I/O Port Status", "class": None},
    "C40": {"name": "Registering a Temperature Sensor Number", "class": None},
    "C41": {"name": "Deleting a Registered Temperature Sensor", "class": None},
    "C42": {"name": "Reading the Temperature Sensor SN and Number", "class": None},
    "C43": {"name": "Setting a Temperature Value for the High/Low Temperature Alarm and Logical Name", "class": None},
    "C44": {"name": "Reading Temperature Sensor Parameters", "class": None},
    "C46": {"name": "Checking Temperature Sensor Parameters", "class": None},
    "D10": {"name": "Authorizing an iButton key", "class": None},
    "D11": {"name": "Authorizing iButton Keys in Batches", "class": None},
    "D12": {"name": "Checking iButton Authorization", "class": None},
    "D13": {"name": "Reading an Authorized iButton Key", "class": None},
    "D14": {"name": "Deleting an Authorized iButton Key", "class": None},
    "D15": {"name": "Deleting Authorized iButton Keys in Batches", "class": None},
    "D16": {"name": "Checking the Checksum of the Authorized iButton ID Database", "class": None},
    "D34": {"name": "Setting Idling Time", "class": None},
    "D71": {"name": "Setting GPS Data Filtering", "class": None},
    "D72": {"name": "Setting Output Triggering", "class": None},
    "D73": {"name": "Allocating GPRS Cache and GPS LOG Storage Space", "class": None},
    "E91": {"name": "Reading Device's Firmware Version and SN", "class": None},
    "F01": {"name": "Restarting the GSM Module", "class": None},
    "F02": {"name": "Restarting the GPS Module", "class": None},
    "F08": {"name": "Setting the Mileage and Run Time", "class": None},
    "F09": {"name": "Deleting SMS/GPRS Cache Data", "class": None},
    "F11": {"name": "Restoring Initial Settings", "class": None},
}


def command_to_object(direction, command_type, payload):
    logger.debug("commant type: %s, with payload %s", command_type, payload)
    if command_type in COMMAND_LIST and COMMAND_LIST[command_type]["class"] is not None:
        return COMMAND_LIST[command_type]["class"](direction, payload)
    return None


def stc_request_location():
    return Command(0, "A10")


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

    for each_command in COMMAND_LIST:
        print("%s: %s" % (each_command, COMMAND_LIST[each_command]))
