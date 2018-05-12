import logging
import psycopg2
import datetime
from sim_chat_lib.geotool_db_api import common

GET_DEVICE_ID_SQL = """SELECT id FROM device_device WHERE imei=$1"""

INSERT_CELLUPDATE_SQL = """
    INSERT INTO
        device_celldata (
            log_time, cell_id, location_area_code, mobile_country_code, mobile_network_code, primary_scrambling_code,
            secondary_synchronisation_code, rx_level, lookup_method, device_id
        )
    VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
    )
"""

INSERT_DEVICEUPDATE_SQL = """ 
 INSERT INTO
   device_deviceupdate (
     device_id, imei, location, true_track, mag_track, ground_speed, altitude, timestamp,
     dilution, num_sats, log_time
  )
  VALUES (
    $1, $2, ST_SetSRID(ST_MakePoint($3, $4), 4326), $5, $6, $7, $8, $9, $10, $11, $12
  )
"""

UPDATE_DEVICE_CACHE_SQL = """ 
 UPDATE
  device_deviceupdatecache
 SET
  location=ST_SetSRID(ST_MakePoint($1, $2), 4326),
  true_track = $3,
  mag_track = $4,
  ground_speed = $5,
  altitude = $6,
  timestamp = $7,
  dilution = $8,
  num_sats = $9
 WHERE
  device_id=$10
"""


async def get_device_id(imei):
    rows = await common.execute_sql_get_a(GET_DEVICE_ID_SQL, imei)
    return rows


def get_insert_cellupdate_coroutine(
        log_time: datetime.datetime, cell_id: int, location_area_code: int, mobile_country_code: int,
        mobile_network_code: int,
        primary_scrambling_code: int, secondary_sychronisation_code: int,
        rx_level: str,
        lookup_method: str,
        device_id: int,
):
    return common.execute_sql_a(
        INSERT_CELLUPDATE_SQL,
        log_time, cell_id, location_area_code, mobile_country_code, mobile_network_code,
        primary_scrambling_code, secondary_sychronisation_code, rx_level, lookup_method,
        device_id
    )


def get_insert_deviceupdate_coroutine(
        device_id: int, imei: str, latitude: float, longitude: float, true_track: int, mag_track: int,
        ground_speed: int, altitude: float, timestamp: datetime.datetime,
        dilution: float, num_sats: int, log_time: datetime.datetime
):
    return common.execute_sql_a(
        INSERT_DEVICEUPDATE_SQL,
        device_id, imei, latitude, longitude, true_track,
        mag_track, ground_speed, altitude, timestamp, dilution,
        num_sats, log_time,

    )


def get_update_deviceupdatecache_coroutine(
        latitude: float, longitude: float, true_track: float, mag_track: int, ground_speed: int, altitude: float,
        timestamp: datetime.datetime, dilution: float, num_sats: int, device_id: int
):
    return common.execute_sql_a(
        UPDATE_DEVICE_CACHE_SQL,
        latitude, longitude, true_track,
        mag_track, ground_speed, altitude, timestamp, dilution,
        num_sats, device_id

    )


if __name__ == '__main__':
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    import time
    import traceback
    import datetime

    print(get_device_id("33330407"))
    print(get_insert_deviceupdate_coroutine(25, "0407", 0, 0, 0, 0, 0, 0, datetime.datetime.now(), 1, 9, datetime.datetime.now()))
    print(get_update_deviceupdatecache_coroutine(0, 0, 0, 0, 0, 0, datetime.datetime.now(), 1, 9, 25))

