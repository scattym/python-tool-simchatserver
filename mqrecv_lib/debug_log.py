import datetime
import json
import logging

import aio_pika
import pytz

from geotool_db_api.debug_log_api import get_insert_debug_log_coroutine
from mqrecv_lib.common import MQ_USER, MQ_PASS, MQ_HOST
from geotool_db_api.device_api import get_device_id

logger = logging.getLogger(__name__)


async def main_debug_log(loop):
    connection = await aio_pika.connect_robust("amqp://{}:{}@{}/".format(MQ_USER, MQ_PASS, MQ_HOST), loop=loop)

    queue_name = "debug_log"

    # Creating channel
    channel = await connection.channel()    # type: aio_pika.Channel

    # Declaring queue
    queue = await channel.declare_queue(queue_name)   # type: aio_pika.Queue
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

            logger.debug("Device id is %s", device_id)
            try:
                log_time = datetime.datetime.strptime(data["log_time"], "%Y-%m-%d %H:%M:%SZ")
            except ValueError as _:
                log_time = datetime.datetime.strptime(data["log_time"], "%Y-%m-%d %H:%M:%S.%f")
            log_time = pytz.utc.localize(log_time)
            if device_id:
                loop.create_task(
                    get_insert_debug_log_coroutine(
                        log_time,
                        data["direction"],
                        data["data"],
                        int(device_id),
                    )
                )

            if queue.name in message.body.decode():
                break