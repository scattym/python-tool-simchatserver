import datetime
import logging
from sim_chat_lib.report import Report

logger = logging.getLogger(__name__)


def safe_field_get(gprs, field):
    try:
        field_value = gprs.enclosed_data[field]
        if field == "date_time":
            return field_value
        else:
            return field_value.decode()

    except AttributeError as err:
        logger.debug("Failed to get field %s, returning None", field)
    return None


def gprs_to_report(gprs):
    if gprs and gprs.enclosed_data:
        report = Report()
        report.imei = gprs.imei.decode()
        report.gps_longitude = safe_field_get(gprs, "longitude")
        report.gps_latitude = safe_field_get(gprs, "latitude")
        report.direction = safe_field_get(gprs, "direction")
        report.speed = safe_field_get(gprs, "speed")
        report.altitude = safe_field_get(gprs, "altitude")
        report.horizontal_accuracy = safe_field_get(gprs, "horizontal_accuracy")
        report.num_sats = safe_field_get(gprs, "num_sats")
        report.timestamp = safe_field_get(gprs, "date_time")

        report.firmware_version = gprs.enclosed_data.get_firmware_version()
        report.serial_number = gprs.enclosed_data.get_serial_number()

        logger.debug(gprs.enclosed_data.get_battery_voltage())
        report.battery_voltage = gprs.enclosed_data.get_battery_voltage()
        report.battery_level = gprs.enclosed_data.get_battery_level()
        logger.debug(gprs.enclosed_data.get_battery_level())
        gprs.enclosed_data.get_base_station_info()
        base_station_info = gprs.enclosed_data.get_base_station_info()
        if base_station_info:
            report.mcc = base_station_info["mcc"].decode()
            logger.debug(report.mcc)
            report.mnc = base_station_info["mnc"].decode()
            logger.debug(report.mnc)
            report.lac = base_station_info["lac"].decode()
            logger.debug(report.lac)
            report.ci = base_station_info["ci"].decode()
            logger.debug(report.ci)
            report.rx_level = base_station_info["gsm_signal_strength"].decode()
            logger.debug(report.rx_level)
        report.event_type = gprs.enclosed_data.get_event_name()
        if report.event_type == "RFID":
            report.license_data = safe_field_get(gprs, "assisted_event_info")
        return report
    return None


def file_download_to_report(imei, file_download):
    report = Report()
    report.imei = imei.decode()
    report.file_name = file_download.file_name.decode()
    report.file_data = file_download.return_file_contents()
    return report


def event_to_report(imei, event_text):
    report = Report()
    report.imei = imei.decode()
    report.event_type = event_text
    report.timestamp = datetime.datetime.utcnow()
    return report
