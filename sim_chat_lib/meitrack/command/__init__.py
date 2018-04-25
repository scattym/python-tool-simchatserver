#!/usr/bin/env python
import logging

import sys
import time

from sim_chat_lib.meitrack import event
from sim_chat_lib.meitrack.command.command_AAA import TrackerCommand
from sim_chat_lib.meitrack.command.command_E91 import RequestDeviceInfoCommand
from sim_chat_lib.meitrack.command.common import Command
from sim_chat_lib.meitrack.error import GPRSParameterError

logger = logging.getLogger(__name__)

COMMAND_LIST = {
    b"A10": {"name": "Real-Time Location Query", "class": None},
    b"A11": {"name": "Setting a Heartbeat Packet Reporting Interval", "class": None},
    b"A12": {"name": "Tracking by Time Interval", "class": None},
    b"A13": {"name": "Setting the Cornering Report Function", "class": None},
    b"A14": {"name": "Tracking by Distance", "class": None},
    b"A15": {"name": "Setting the Parking Scheduled Tracking Function", "class": None},
    b"A16": {"name": "Enabling the Parking Scheduled Tracking Function", "class": None},
    b"A21": {"name": "Setting GPRS Parameters", "class": None},
    b"A22": {"name": "Setting the DNS Server IP Address", "class": None},
    b"A23": {"name": "Setting the Standby GPRS Server", "class": None},
    b"A70": {"name": "Reading All Authorized Phone Numbers", "class": None},
    b"A71": {"name": "Setting Authorized Phone Numbers", "class": None},
    b"A73": {"name": "Setting the Smart Sleep Mode", "class": None},
    b"AAA": {"name": "Automatic Event Report", "class": TrackerCommand},
    b"AFF": {"name": "Deleting a GPRS Event in the Buffer", "class": None},
    b"B05": {"name": "Setting a Geo-Fence", "class": None},
    b"B06": {"name": "Deleting a Geo-Fence", "class": None},
    b"B07": {"name": "Setting the Speeding Alarm Function", "class": None},
    b"B08": {"name": "Setting the Towing Alarm Function", "class": None},
    b"B21": {"name": "Setting the Anti-Theft Function", "class": None},
    b"B34": {"name": "Setting a Log Interval", "class": None},
    b"B35": {"name": "Setting the SMS Time Zone", "class": None},
    b"B36": {"name": "Setting the GPRS Time Zone", "class": None},
    b"B60": {"name": "Checking the Engine First to Determine Tracker Running Status", "class": None},
    b"B99": {"name": "Setting Event Authorization", "class": None},
    b"C01": {"name": "Controlling Output Status", "class": None},
    b"C02": {"name": "Notifying the Tracker of Sending an SMS", "class": None},
    b"C03": {"name": "Setting a GPRS Event Transmission Mode", "class": None},
    b"C08": {"name": "Setting I/O Port Status", "class": None},
    b"C40": {"name": "Registering a Temperature Sensor Number", "class": None},
    b"C41": {"name": "Deleting a Registered Temperature Sensor", "class": None},
    b"C42": {"name": "Reading the Temperature Sensor SN and Number", "class": None},
    b"C43": {"name": "Setting a Temperature Value for the High/Low Temperature Alarm and Logical Name", "class": None},
    b"C44": {"name": "Reading Temperature Sensor Parameters", "class": None},
    b"C46": {"name": "Checking Temperature Sensor Parameters", "class": None},
    b"D10": {"name": "Authorizing an iButton key", "class": None},
    b"D11": {"name": "Authorizing iButton Keys in Batches", "class": None},
    b"D12": {"name": "Checking iButton Authorization", "class": None},
    b"D13": {"name": "Reading an Authorized iButton Key", "class": None},
    b"D14": {"name": "Deleting an Authorized iButton Key", "class": None},
    b"D15": {"name": "Deleting Authorized iButton Keys in Batches", "class": None},
    b"D16": {"name": "Checking the Checksum of the Authorized iButton ID Database", "class": None},
    b"D34": {"name": "Setting Idling Time", "class": None},
    b"D71": {"name": "Setting GPS Data Filtering", "class": None},
    b"D72": {"name": "Setting Output Triggering", "class": None},
    b"D73": {"name": "Allocating GPRS Cache and GPS LOG Storage Space", "class": None},
    b"E91": {"name": "Reading Device's Firmware Version and SN", "class": RequestDeviceInfoCommand},
    b"F01": {"name": "Restarting the GSM Module", "class": None},
    b"F02": {"name": "Restarting the GPS Module", "class": None},
    b"F08": {"name": "Setting the Mileage and Run Time", "class": None},
    b"F09": {"name": "Deleting SMS/GPRS Cache Data", "class": None},
    b"F11": {"name": "Restoring Initial Settings", "class": None},
}


def command_to_object(direction, command_type, payload):
    logger.debug("command type: %s, with payload %s", command_type, payload)
    if command_type in COMMAND_LIST and COMMAND_LIST[command_type]["class"] is not None:
        return COMMAND_LIST[command_type]["class"](direction, payload)
    else:
        return Command(direction, payload)


def stc_request_file_download(file_name):
    return Command(0, b"D00," + str(file_name).encode() + b",0")


def stc_request_take_photo(camera_number, file_name):
    if file_name is None:
        file_name = "camera-{}-{}.jpg".format(camera_number, int(time.time()))
    return Command(0, b"D03," + str(camera_number).encode() + b"," + str(file_name).encode())


def stc_request_photo_list():
    return Command(0, b"D01,0")


def stc_request_location():
    return Command(0, b"A10")


def stc_set_heartbeat(minutes=0):
    if minutes < 0 or minutes > 65535:
        raise GPRSParameterError("Heartbeat must be between 0 and 65535. Was %s" % (minutes,))
    return Command(0, b"A11,%b" % (str(minutes).encode(),))


def stc_set_tracking_by_time_interval(deci_seconds=0):
    if deci_seconds < 0 or deci_seconds > 65535:
        raise GPRSParameterError("Time interval must be between 0 and 65535. Was %s" % (deci_seconds,))
    return Command(0, b"A12,%b" % (str(deci_seconds).encode(),))


def stc_set_cornering_angle(angle=0):
    if angle < 0 or angle > 359:
        raise GPRSParameterError("Cornering angle must be between 0 and 359. Was %s" % (angle,))
    return Command(0, b"A13,%s" % (str(angle).encode(),))


def stc_set_tracking_by_distance(meters=0):
    if meters < 0 or meters > 65535:
        raise GPRSParameterError("Tracking by distance must be between 0 and 65535. Was %s" % (meters,))
    return Command(0, b"A14,%s" % (str(meters).encode(),))


def stc_request_info():
    return Command(0, b"E91")


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
