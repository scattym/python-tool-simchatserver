import datetime
import json
import logging

import aio_pika
import pytz

from mqrecv_lib.common import MQ_USER, MQ_PASS, MQ_HOST
from geotool_db_api.device_api import get_device_id, get_insert_deviceupdate_coroutine, \
    get_update_deviceupdatecache_coroutine

logger = logging.getLogger(__name__)

async def main_gps_update(loop):
    connection = await aio_pika.connect_robust("amqp://{}:{}@{}/".format(MQ_USER, MQ_PASS, MQ_HOST), loop=loop)

    queue_name = "gps_update"

    # Creating channel
    channel = await connection.channel()  # type: aio_pika.Channel

    # Declaring queue
    queue = await channel.declare_queue(queue_name)  # type: aio_pika.Queue
    imei_map = {}

    async for message in queue:
        with message.process():
            logger.info(message.body)
            data = json.loads(message.body)
            if data.get("imei", None):
                if imei_map.get(data["imei"]):
                    device_id = imei_map.get(data["imei"])
                else:
                    device_id = await get_device_id(data["imei"])
                    if device_id:
                        imei_map[data["imei"]] = device_id
            elif data.get("device", None):
                device_id = data["device"]

            ####
            # Handle GPS UPDATE MESSAGES
            if data.get("location") is not None or data.get("latitude") is not None:
                # Handle gps coming in as a single field
                # "SRID=4326;POINT (151.07571 -33.636995)",
                location = data.get("location", None)
                if location:
                    bracket_open = location.find('(')
                    bracket_close = location.find(')')
                    logger.debug(location[bracket_open + 1:bracket_close])
                    longitude, latitude = location[bracket_open + 1:bracket_close].split(" ", 1)
                else:
                    longitude = data.get("longitude")
                    latitude = data.get("latitude")

                logger.debug("Device id is %s", device_id)
                if "." not in data["timestamp"]:
                    data["timestamp"] = "{}.0".format(data["timestamp"])
                timestamp = datetime.datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                if "." not in data["log_time"]:
                    data["log_time"] = "{}.0".format(data["log_time"])

                log_time = datetime.datetime.strptime(data["log_time"], "%Y-%m-%d %H:%M:%S.%f")
                log_time = pytz.utc.localize(log_time)
                timestamp = pytz.utc.localize(timestamp)

                if device_id:
                    insert_coroutine = get_insert_deviceupdate_coroutine(
                        device_id,
                        data["imei"],
                        float(longitude),
                        float(latitude),
                        int(data["true_track"]),
                        int(0),
                        int(data["ground_speed"]),
                        float(data["altitude"]),
                        timestamp,
                        float(data["dilution"]),
                        int(data["num_sats"]),
                        log_time,
                    )
                    loop.create_task(insert_coroutine)
                    # loop.run_until_complete(insert_coroutine)

                    update_coroutine = get_update_deviceupdatecache_coroutine(
                        float(longitude), float(latitude), int(data["true_track"]),
                        int(0), int(data["ground_speed"]), float(data["altitude"]),
                        timestamp, float(data["dilution"]), int(data["num_sats"]),
                        device_id,
                    )
                    loop.create_task(update_coroutine)
                    # loop.run_until_complete(update_coroutine)
            else:
                logger.error("Unknown command %s", data)

            if queue.name in message.body.decode():
                break
