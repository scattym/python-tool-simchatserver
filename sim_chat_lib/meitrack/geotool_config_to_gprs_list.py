import logging

from meitrack import build_message
from sim_chat_lib.report import event_to_report

logger = logging.getLogger(__name__)


def config_to_gprs(config, imei):
    gprs_list = []
    event_report_list = []
    if config.get("heartbeat_interval_en", False) is True and config.get("heartbeat_interval") is not None:
        gprs = build_message.stc_set_heartbeat_interval(imei, config.get("heartbeat_interval"))
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set heartbeat interval")
        event_report_list.append(event_report)

    if config.get("time_interval_en", False) is True and config.get("time_interval") is not None:
        gprs = build_message.stc_set_tracking_by_time_interval(imei, config.get("time_interval"))
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set time interval")
        event_report_list.append(event_report)

    if config.get("cornering_angle_en", False) is True and config.get("cornering_angle") is not None:
        gprs = build_message.stc_set_cornering_angle(imei, config.get("cornering_angle"))
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set cornering angle")
        event_report_list.append(event_report)

    if config.get("tracking_by_distance_en", False) is True and config.get("tracking_by_distance") is not None:
        gprs = build_message.stc_set_tracking_by_distance(imei, config.get("tracking_by_distance"))
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set tracking by distance")
        event_report_list.append(event_report)

    if config.get("time_zone_offset_minutes_en", False) is True and config.get("time_zone_offset_minutes") is not None:
        gprs = build_message.stc_set_time_zone(imei, config.get("time_zone_offset_minutes"))
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set timezone offset")
        event_report_list.append(event_report)

    if config.get("driving_license_type_en", False) is True:
        driving_license_type = config.get("driving_license_type")
        if driving_license_type is None:
            driving_license_type = ""
        gprs = build_message.stc_set_driver_license_type(imei, driving_license_type)
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set driving license type")
        event_report_list.append(event_report)

    if config.get("fatigue_driving_en", False) is True and config.get("fatigue_driving_consecutive_driving_time") is not None or \
            config.get("fatigue_driving_alert_time") is not None or \
            config.get("fatigue_driving_acc_off_time_mins") is not None:
        consecutive = config.get("fatigue_driving_consecutive_driving_time") or 480
        alert = config.get("fatigue_driving_alert_time") or 300
        acc_off = config.get("fatigue_driving_acc_off_time_mins") or 0
        gprs = build_message.stc_set_fatigue_driving_alert_time(
            imei,
            consecutive,
            alert,
            acc_off
        )
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set drivers license type")
        event_report_list.append(event_report)

    if config.get("idle_alert_en", False) is True and config.get("idle_alert_consecutive_speed_time") is not None or \
            config.get("idle_alert_speed_kmh") is not None or \
            config.get("idle_alert_alert_time") is not None:
        consecutive = config.get("idle_alert_consecutive_speed_time") or 480
        speed = config.get("fatigue_driving_acc_off_time_mins") or 0
        alert_time = config.get("idle_alert_alert_time") or 300

        gprs = build_message.stc_set_idle_alert_time(
            imei,
            consecutive,
            speed,
            alert_time,
        )
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set idle alert parameters")
        event_report_list.append(event_report)

    if config.get("speeding_alert_en", False) is True and config.get("speeding_alert_speed") is not None or \
            config.get("speeding_alert_disabled") is not None:
        speed = config.get("speeding_alert_speed") or 480
        disabled = config.get("speeding_alert_disabled") or True
        gprs = build_message.stc_set_speeding_alert(
            imei,
            speed,
            disabled,
        )
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set speeding parameters")
        event_report_list.append(event_report)

    if config.get("driving_license_validity_time_en", False) is True and config.get("driving_license_validity_time") is not None:
        gprs = build_message.stc_set_driver_license_validity_time(
            imei,
            config.get("driving_license_validity_time")
        )
        gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set driving license validity time")
        event_report_list.append(event_report)

    if config.get("peripheral_configuration_en", False) is True and config.get("peripheral_configuration") is not None:
        config_list = []
        if config["peripheral_configuration"].get("device_type") == 9:
            for key, val in config["peripheral_configuration"].items():
                if 'device_' in key:
                    if val is not None:
                        try:
                            device_id = int(key.split('_')[1])
                            config_list.append([device_id, val])
                        except ValueError as _:
                            logger.error("Unable to find device id from key %s", key)
            if config_list:
                gprs = build_message.stc_set_io_device_params(imei, b"A78", config_list)
                gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set peripheral config")
        event_report_list.append(event_report)

    if config.get("camera_setup_en", False) is True:
        if config.get("camera_setup") and config["camera_setup"].get("events"):

            for event in config["camera_setup"]["events"]:
                gprs = build_message.stc_set_snapshot_parameters(
                    imei,
                    event["event_code"],
                    event["interval"],
                    event["count"],
                    event["upload"],
                    event["delete"]
                )
                gprs_list.append(gprs)
        event_report = event_to_report(imei, "Set camera snapshot config")
        event_report_list.append(event_report)

    return gprs_list, event_report_list
