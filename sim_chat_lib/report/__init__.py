#!/usr/bin/env python
import datetime


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
        self.event_type = None
        self.file_name = None
        self.file_data = None


class MeitrackConfigRequest(object):
    def __init__(self):
        self.imei = None
        self.response = None

    def __str__(self):
        return "%s-%s" % (self.imei, self.response)


if __name__ == "__main__":
    report = Report()
    report.imei = "testimei"
