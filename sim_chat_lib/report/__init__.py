#!/usr/bin/env python
import datetime
import logging

import geotool_api
from geotool_api import meitrack_file_add_packet
from geotool_api import add_debug_log
from geotool_api.driver_api import add_driver_log_by_license
from license.cardreader import License

logger = logging.getLogger(__name__)

DEBUG_LOG_DIRECTION_CLIENT_TO_SERVER = '0'
DEBUG_LOG_DIRECTION_SERVER_TO_CLIENT = '1'


class BaseReport(object):
    def __init__(self):
        self._imei = None
        self.timestamp = None
        pass

    def execute_post(self, log_time):
        pass

    def response_to_chat_dict(self, response_type, response):
        return {
            "type": response_type,
            "imei": self.imei,
            "response": response
        }

    @property
    def imei(self):
        return self._imei

    @imei.setter
    def imei(self, value):
        try:
            self._imei = value.decode()
        except AttributeError as _:
            self._imei = value


class DigitalPinReport(BaseReport):
    def __init__(self):
        super().__init__()
        self.pin_map = None
        self.timestamp = None

    def execute_post(self, log_time):
        super().execute_post(log_time)
        result = geotool_api.add_digital_pin_states(self.imei, self.pin_map, self.timestamp)
        if not result:
            logger.error("Unable to log the event. Result: %s", result)
            logger.debug(result)
        return self.response_to_chat_dict("digital_pin_update", result)


class AnaloguePinReport(BaseReport):
    def __init__(self):
        super().__init__()
        self.pin_map = None
        self.timestamp = None

    def execute_post(self, log_time):
        super().execute_post(log_time)
        result = geotool_api.add_analogue_pin_states(self.imei, self.pin_map, self.timestamp)
        if not result:
            logger.error("Unable to log the event. Result: %s", result)
            logger.debug(result)
        return self.response_to_chat_dict("analogue_pin_update", result)


class DebugLogReport(BaseReport):
    def __init__(self):
        super().__init__()
        self.data = None
        self.direction = None

    def execute_post(self, log_time):
        super().execute_post(log_time)
        result = add_debug_log(self.imei, self.direction, self.data, log_time)
        if not result:
            logger.error("Unable to log the event. Result: %s", result)
            logger.debug(result)
        return self.response_to_chat_dict("debug_log", result)


class AAAReport(BaseReport):
    def __init__(self):
        super().__init__()
        self.gps_latitude = None
        self.gps_longitude = None
        self.num_sats = None
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

    def execute_post(self, log_time):
        pass


# NOTE: Not currently used
class LicenseReadReport(AAAReport):
    def __init__(self):
        super().__init__()
        self.license = None
        self.timestamp = datetime.datetime.utcnow()

    def execute_post(self, log_time):
        super().execute_post(log_time)
        result = add_driver_log_by_license(self.imei, self.license)
        if not result:
            logger.error("Unable to log the event. Result: %s", result)
            logger.debug(result)
        return result


class FileFragmentReport(BaseReport):
    def __init__(self):
        super().__init__()
        self.file_name = None
        self.num_packets = None
        self.packet_number = None
        self.file_bytes = None
        self.timestamp = datetime.datetime.utcnow()

    def execute_post(self, log_time):
        result = geotool_api.add_event_log(
            self.imei,
            self.timestamp,
            2,
            "{} {} of {}".format(self.file_name, self.packet_number+1, self.num_packets),
            log_time,
        )
        if not result:
            logger.error("Unable to log the event. Result: %s", result)
            logger.debug(result)
        return meitrack_file_add_packet(
            self.imei,
            self.file_name,
            self.num_packets,
            self.packet_number,
            self.file_bytes,
            log_time,
        )


class FirmwareBinaryRequestReport(BaseReport):
    def __init__(self):
        super().__init__()

    def execute_post(self, log_time):
        result = geotool_api.firmware_api.get_firmware_by_imei(self.imei)

        if not result:
            logger.error("Unable to get the firmware binary")
        return self.response_to_chat_dict("firmware_binary", result)


class FirmwareVersionRequestReport(BaseReport):
    def __init__(self):
        super().__init__()

    def execute_post(self, log_time):
        result = geotool_api.firmware_api.get_firmware_version_by_imei(self.imei)
        print(result)
        if not result:
            logger.error("Unable to get firmware version: %s", result)
        return self.response_to_chat_dict("firmware_version", result)


class Report(object):
    def __init__(self):
        self.imei = None
        self.gps_latitude = None
        self.gps_longitude = None
        self.num_sats = None
        self.timestamp = datetime.datetime.utcnow()
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
        self.taxi_data = None


class MeitrackConfigRequest(object):
    def __init__(self):
        self.imei = None
        self.response = None

    def __str__(self):
        return "%s-%s" % (self.imei, self.response)


def event_to_report(imei, event_text):
    report = Report()
    try:
        report.imei = imei.decode()
    except AttributeError as _:
        report.imei = imei
    try:
        report.event_description = event_text.decode()
    except AttributeError as _:
        report.event_description = event_text
    report.timestamp = datetime.datetime.utcnow()
    return report


if __name__ == "__main__":
    report = Report()
    report.imei = "testimei"
