import datetime
import logging
from sim_chat_lib.report import Report, FileFragmentReport, FirmwareBinaryRequestReport, FirmwareVersionRequestReport, \
    DigitalPinReport, AnaloguePinReport
from sim_chat_lib.report import LicenseReadReport

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
        file_name, num_packets, packet_number, file_bytes = gprs.enclosed_data.get_file_data()
        if file_name and file_bytes:
            file_frag_report = FileFragmentReport()
            file_frag_report.imei = gprs.imei.decode()
            file_frag_report.file_name = file_name.decode()
            file_frag_report.num_packets = int(num_packets.decode())
            file_frag_report.packet_number = int(packet_number.decode())
            file_frag_report.file_bytes = file_bytes
            file_frag_report.timestamp = safe_field_get(gprs, "date_time")
            return [file_frag_report]
        else:
            report_list = []
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

            report.firmware_version = safe_field_get(gprs, "firmware_version")
            report.serial_number = safe_field_get(gprs, "serial_number")

            logger.debug("Battery voltage is %s", gprs.enclosed_data.get_battery_voltage())
            report.battery_voltage = gprs.enclosed_data.get_battery_voltage()
            logger.debug("Battery level is %s", gprs.enclosed_data.get_battery_level())
            report.battery_level = gprs.enclosed_data.get_battery_level()
            logger.debug(gprs.enclosed_data.get_battery_level())
            gprs.enclosed_data.get_base_station_info()
            base_station_info = gprs.enclosed_data.get_base_station_info()
            if base_station_info:
                report.mcc = base_station_info["mcc"].decode()
                logger.debug("mcc is %s", report.mcc)
                report.mnc = base_station_info["mnc"].decode()
                logger.debug("mnc is %s", report.mnc)
                report.lac = base_station_info["lac"].decode()
                logger.debug("lac is %s", report.lac)
                report.ci = base_station_info["ci"].decode()
                logger.debug("ci is %s", report.ci)
                report.rx_level = base_station_info["gsm_signal_strength"].decode()
                logger.debug("gsm_signal_strength is %s", report.rx_level)
            report.event_id = gprs.enclosed_data.get_event_id()
            report.event_description = gprs.enclosed_data.get_event_name()
            if report.event_description == "RFID":
                report.license_data = safe_field_get(gprs, "rfid")

            report.taxi_data = gprs.enclosed_data.get_taxi_meter_data()
            report_list.append(report)

            digital_pins = gprs.enclosed_data.get_digital_pin_states()
            if digital_pins:
                digital_pin_report = DigitalPinReport()
                digital_pin_report.imei = gprs.imei
                digital_pin_report.timestamp = safe_field_get(gprs, "date_time")
                digital_pin_report.pin_map = digital_pins
                report_list.append(digital_pin_report)

            analogue_pins = gprs.enclosed_data.get_analogue_pin_states()
            if analogue_pins:
                analogue_pin_report = AnaloguePinReport()
                analogue_pin_report.imei = gprs.imei
                analogue_pin_report.timestamp = safe_field_get(gprs, "date_time")
                analogue_pin_report.pin_map = analogue_pins
                report_list.append(analogue_pin_report)

            return report_list
    return None


def file_download_to_report(imei, file_download):
    report = Report()
    report.imei = imei.decode()
    report.file_name = file_download.file_name.decode()
    report.file_data = file_download.return_file_contents()
    return report


def get_firmware_binary_report(imei):
    report = FirmwareBinaryRequestReport()
    report.imei = imei.decode()
    return report


def get_firmware_version_report(imei):
    report = FirmwareVersionRequestReport()
    report.imei = imei.decode()
    return report
