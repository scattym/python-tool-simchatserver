import logging
from sim_chat_lib.report import Report

logger = logging.getLogger(__name__)


def safe_field_get(gprs, field):
    try:
        field_value = gprs.enclosed_data[field]
        if field != "date_time":
            return field_value.decode()
        else:
            return field_value
    except AttributeError as err:
        logger.error("Failed to get field %s, returning None", field)
    return None


def gprs_to_report(gprs):
    if gprs and gprs.enclosed_data:
        report = Report()
        report.imei = gprs.imei.decode()
        report.gps_longitude = safe_field_get(gprs, "longitude")
        report.gps_latitude = safe_field_get(gprs, "latitude")
        report.num_sats = safe_field_get(gprs, "num_sats")
        report.timestamp = safe_field_get(gprs, "date_time")
        logger.debug(gprs.enclosed_data.get_battery_voltage())
        report.battery_voltage = gprs.enclosed_data.get_battery_voltage()
        gprs.enclosed_data.get_battery_level()
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
        report.event_type = gprs.enclosed_data.get_event_type()
        return report
    return None


def file_download_to_report(imei, file_download):
    report = Report()
    report.imei = imei
    report.file_name = file_download.file_name
    report.file_data = file_download.return_file_contents()
    return report
