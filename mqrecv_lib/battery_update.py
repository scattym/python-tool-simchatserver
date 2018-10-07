import json
import logging

import aio_pika

from mqrecv_lib.common import MQ_USER, MQ_PASS, MQ_HOST
from geotool_db_api.device_api import get_device_id
from geotool_db_api.battery_api import get_update_battery_coroutine

logger = logging.getLogger(__name__)


async def main_battery_update(loop):
    connection = await aio_pika.connect_robust("amqp://{}:{}@{}/".format(MQ_USER, MQ_PASS, MQ_HOST), loop=loop)

    queue_name = "battery_update"

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
            elif data.get("primary_key") is not None:
                device_id = data.get("primary_key")

            logger.debug("Device id is %s", device_id)

            ####
            # Handle GPS UPDATE MESSAGES
            if data.get("battery_level") is not None:

                # (device_id: int, battery_in_use: bool, battery_voltage: str, battery_level: str):
                insert_coroutine = get_update_battery_coroutine(
                    device_id,
                    None,
                    data.get("battery_voltage"),
                    data.get("battery_level")
                )
                loop.create_task(insert_coroutine)
                # loop.run_until_complete(update_coroutine)
            else:
                logger.error("Unknown command %s", data)

            if queue.name in message.body.decode():
                break