import logging
from sim_chat_lib.report import Report

logger = logging.getLogger(__name__)


def safe_field_get(gprs, field):
    try:
        return gprs.enclosed_data[field]
    except AttributeError as err:
        logger.error("Failed to get field %s, returning None", field)
    return None


def gprs_to_report(gprs):
    if gprs and gprs.enclosed_data:
        report = Report()
        report.imei = gprs.imei
        report.gps_longitude = safe_field_get(gprs, "longitude")
        report.gps_latitude = safe_field_get(gprs, "latitude")
        report.num_sats = safe_field_get(gprs, "num_sats")
        report.timestamp = safe_field_get(gprs, "date_time")
        logger.debug(gprs.enclosed_data.get_battery_voltage())
        report.battery_voltage = gprs.enclosed_data.get_battery_voltage()
        gprs.enclosed_data.get_battery_level()
        report.battery_level = gprs.enclosed_data.get_battery_level()
        gprs.enclosed_data.get_base_station_info()
        base_station_info = gprs.enclosed_data.get_base_station_info()
        if base_station_info:
            report.mcc = base_station_info["mcc"]
            report.mnc = base_station_info["mnc"]
            report.lac = base_station_info["lac"]
            report.ci = base_station_info["ci"]
            report.rx_level = base_station_info["gsm_signal_strength"]
        report.event_type = gprs.enclosed_data.get_event_type()
        return report
    return None
