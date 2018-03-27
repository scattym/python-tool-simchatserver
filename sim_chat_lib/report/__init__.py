#!/usr/bin/env python
import datetime


class Report(object):
    def __init__(self):
        self.imei = None
        self.gps_latitude = None
        self.gps_longitude = None
        self.num_sats = None
        self.timestamp = datetime.datetime.now()


if __name__ == "__main__":
    report = Report()
    report.imei = "testimei"
