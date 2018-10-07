import json
import logging

import aio_pika

from mqrecv_lib.common import MQ_USER, MQ_PASS, MQ_HOST
from geotool_db_api.device_api import get_device_id, get_update_firmware_coroutine

logger = logging.getLogger(__name__)


async def main_firmware_update(loop):
    connection = await aio_pika.connect_robust("amqp://{}:{}@{}/".format(MQ_USER, MQ_PASS, MQ_HOST), loop=loop)

    queue_name = "firmware_update"

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
            # manufacturer: str, model: str, revision: str, serial: str, running_version: str, imei: str
            loop.create_task(get_update_firmware_coroutine(
                data["manufacturer"], data["model"], data["revision"], data["serial"], data["running_version"],
                device_id
            ))

            if queue.name in message.body.decode():
                break