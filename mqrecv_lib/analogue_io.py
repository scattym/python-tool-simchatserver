import datetime
import json
import logging

import aio_pika
import pytz

from geotool_db_api.input_output_api import get_insert_analogue_io_coroutine, get_update_current_analogue_io_coroutine
from mqrecv_lib.common import MQ_USER, MQ_PASS, MQ_HOST
from geotool_db_api.device_api import get_device_id

logger = logging.getLogger(__name__)


async def main_analogue_io(loop):
    connection = await aio_pika.connect_robust("amqp://{}:{}@{}/".format(MQ_USER, MQ_PASS, MQ_HOST), loop=loop)

    queue_name = "analogue_io"

    # Creating channel
    channel = await connection.channel()  # type: aio_pika.Channel

    # Declaring queue
    queue = await channel.declare_queue(queue_name)  # type: aio_pika.Queue
    imei_map = {}

    async for message in queue:
        with message.process():
            logger.log(15, message.body)
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

            ####
            # Handle GPS UPDATE MESSAGES
            if data.get("pin") is not None:
                if '.' not in data["timestamp"]:
                    data["timestamp"] = "{}.0".format(data["timestamp"])
                timestamp = datetime.datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                timestamp = pytz.utc.localize(timestamp)
                insert_coroutine = get_insert_analogue_io_coroutine(
                    device_id,
                    int(data.get("pin")),
                    float(data.get("value")),
                    timestamp
                )
                loop.create_task(insert_coroutine)
                # loop.run_until_complete(update_coroutine)
            else:
                logger.error("Unknown command %s", data)

            if queue.name in message.body.decode():
                break


async def main_current_analogue_io(loop):
    connection = await aio_pika.connect_robust("amqp://{}:{}@{}/".format(MQ_USER, MQ_PASS, MQ_HOST), loop=loop)

    queue_name = "current_analogue_io"

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

            logger.debug("Device id is %s", device_id)

            ####
            # Handle GPS UPDATE MESSAGES
            if data.get("pin") is not None:
                if '.' not in data["timestamp"]:
                    data["timestamp"] = "{}.0".format(data["timestamp"])
                timestamp = datetime.datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                timestamp = pytz.utc.localize(timestamp)
                insert_coroutine = get_update_current_analogue_io_coroutine(
                    device_id,
                    int(data.get("pin")),
                    float(data.get("value")),
                    timestamp
                )
                loop.create_task(insert_coroutine)
                # loop.run_until_complete(update_coroutine)
            else:
                logger.error("Unknown command %s", data)

            if queue.name in message.body.decode():
                break