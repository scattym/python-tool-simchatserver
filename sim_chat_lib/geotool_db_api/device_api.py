import logging
import psycopg2
import datetime
from sim_chat_lib.geotool_db_api import common

GET_DEVICE_ID_SQL = """SELECT id FROM device_device WHERE imei=$1"""

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


def get_device_id(imei):
    rows = common.execute_sql_get_a(GET_DEVICE_ID_SQL, imei)
    return rows


def insert_deviceupdate(
        device_id:int, imei:str, latitude:float, longitude:float, true_track:int, mag_track:int, ground_speed:int,
        altitude:float, timestamp:datetime.datetime,
        dilution:float, num_sats:int, log_time:datetime.datetime
):
    result = common.execute_sql_update_a(
        INSERT_DEVICEUPDATE_SQL,
        device_id, imei, latitude, longitude, true_track,
        mag_track, ground_speed, altitude, timestamp, dilution,
        num_sats, log_time,

    )
    return result


def update_deviceupdatecache(
        latitude:float, longitude:float, true_track:float, mag_track:int, ground_speed:int, altitude:float,
        timestamp:datetime.datetime, dilution:float, num_sats:int, device_id:int
):
    result = common.execute_sql_update_a(
        UPDATE_DEVICE_CACHE_SQL,
        latitude, longitude, true_track,
        mag_track, ground_speed, altitude, timestamp, dilution,
        num_sats, device_id

    )
    return result


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
    print(insert_deviceupdate(25, "0407", 0, 0, 0, 0, 0, 0, datetime.datetime.now(), 1, 9, datetime.datetime.now()))
    print(update_deviceupdatecache(0, 0, 0, 0, 0, 0, datetime.datetime.now(), 1, 9, 25))

