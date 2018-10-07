import datetime
import json
import logging

import aio_pika
import pytz

from mqrecv_lib.common import MQ_USER, MQ_PASS, MQ_HOST
from geotool_db_api.device_api import get_device_id, get_insert_cellupdate_coroutine

logger = logging.getLogger(__name__)


async def main_cell_update(loop):
    connection = await aio_pika.connect_robust("amqp://{}:{}@{}/".format(MQ_USER, MQ_PASS, MQ_HOST), loop=loop)

    queue_name = "cell_update"

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
            if "." not in data["log_time"]:
                data["log_time"] = "{}.0".format(data["log_time"])

            try:
                log_time = datetime.datetime.strptime(data["log_time"], "%Y-%m-%d %H:%M:%S.%f")
            except ValueError as _:
                log_time = datetime.datetime.strptime(data["log_time"], "%Y-%m-%d %H:%M:%SZ")
            log_time = pytz.utc.localize(log_time)

            if device_id:
                loop.create_task(
                    get_insert_cellupdate_coroutine(
                        log_time,
                        int(data["cell_id"]),
                        int(data["location_area_code"]),
                        int(data["mobile_country_code"]),
                        int(data["mobile_network_code"]),
                        data.get("primary_scrambling_code", None),
                        data.get("secondary_sychronisation_code", None),
                        data.get("rx_level", None),
                        "0",
                        int(device_id),
                    )
                )

            if queue.name in message.body.decode():
                break