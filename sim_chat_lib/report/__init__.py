#!/usr/bin/env python
import datetime
import logging

import geotool_api
from geotool_api import meitrack_file_add_packet

logger = logging.getLogger(__name__)


class BaseReport(object):
    def __init__(self):
        self.imei = None
        self.timestamp = datetime.datetime.now()
        pass

    def execute_post(self, log_time):
        logger.error("Calling execute post from base class")
        pass


class FileFragmentReport(BaseReport):
    def __init__(self):
        super().__init__()
        self.file_name = None
        self.num_packets = None
        self.packet_number = None
        self.file_bytes = None

    def execute_post(self, log_time):
        result = geotool_api.add_event_log(
            self.imei,
            self.timestamp,
            2,
            "{} {} of {}".format(self.file_name, self.packet_number+1, self.num_packets),
            log_time,
        )
        if not result:
            logger.error("Unable to log the event")
        return meitrack_file_add_packet(
            self.imei,
            self.file_name,
            self.num_packets,
            self.packet_number,
            self.file_bytes
        )


class Report(object):
    def __init__(self):
        self.imei = None
        self.gps_latitude = None
        self.gps_longitude = None
        self.num_sats = None
        self.timestamp = datetime.datetime.now()
        self.battery_voltage = None
        self.battery_level = None
        self.mcc = None
        self.mnc = None
        self.lac = None
        self.ci = None
        self.rx_level = None
        self.event_description = None
        self.event_id = None
        self.file_name = None
        self.file_data = None
        self.firmware_version = None
        self.serial_number = None
        self.license_data = None


class MeitrackConfigRequest(object):
    def __init__(self):
        self.imei = None
        self.response = None

    def __str__(self):
        return "%s-%s" % (self.imei, self.response)


if __name__ == "__main__":
    report = Report()
    report.imei = "testimei"
