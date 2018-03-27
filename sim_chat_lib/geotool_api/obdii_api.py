import requests
import logging
from datetime import datetime
from sim_chat_lib.geotool_api import common

logger = logging.getLogger(__name__)


def create_obdii(device_pk, report_time, engine_rpm, vehicle_speed, throttle_position, intake_air_temperature,
                 run_time, fuel_tank_level, distance_traveled, ambient_air_temperature):
    data = {
        "device": device_pk,
        "report_time": str(report_time),
        "engine_rpm": engine_rpm,
        "vehicle_speed": vehicle_speed,
        "throttle_position": throttle_position,
        "intake_air_temperature": intake_air_temperature,
        "run_time": run_time,
        "fuel_tank_level": fuel_tank_level,
        "distance_traveled": distance_traveled,
        "ambient_air_temperature": ambient_air_temperature
    }
    result = common.post_to_api(common.OBDII_API, data)
    if result and "id" in result:
        return result["id"]
    return None


if __name__ == '__main__':
    log_level = 11 - 2

    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    common.set_api_host("localhost:8000")