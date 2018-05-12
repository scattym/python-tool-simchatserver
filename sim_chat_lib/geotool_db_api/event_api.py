import logging
import psycopg2
import datetime
from sim_chat_lib.geotool_db_api import common

GET_DEVICE_ID_SQL = """SELECT id FROM device_device WHERE imei=$1"""

EVENT_LOG_SQL = """ 
 INSERT INTO event_eventlog (device_id, timestamp, event_description, event_type, log_time, acknowledged_flag)
  VALUES ($1, $2, $3, $4, $5, $6)
"""


def insert_eventlog(
        device_id: int, timestamp: datetime.datetime, event_description: str,
        event_type: str, log_time: datetime.datetime,
):
    result = common.execute_sql_update_a(
        EVENT_LOG_SQL,
            device_id, timestamp, event_description, event_type, log_time, False

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

    print(insert_eventlog(25, datetime.datetime.now(), "test", 0, datetime.datetime.now()))

