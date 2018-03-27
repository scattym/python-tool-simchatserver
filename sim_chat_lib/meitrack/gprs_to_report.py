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
        return report
    return None
