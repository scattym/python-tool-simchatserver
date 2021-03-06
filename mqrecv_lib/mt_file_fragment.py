import base64
import datetime
import json
import logging

import aio_pika

from meitrack.command.common import meitrack_date_to_datetime
from mqrecv_lib.common import MQ_USER, MQ_PASS, MQ_HOST
from geotool_db_api.device_api import get_device_id
from geotool_api.camera_api import add_camera_image

logger = logging.getLogger(__name__)


async def main_mt_file_fragment(loop, file_agg):
    connection = await aio_pika.connect_robust("amqp://{}:{}@{}/".format(MQ_USER, MQ_PASS, MQ_HOST), loop=loop)

    queue_name = "mt_file_fragment"

    # Creating channel
    channel = await connection.channel()    # type: aio_pika.Channel

    # Declaring queue
    queue = await channel.declare_queue(queue_name)   # type: aio_pika.Queue
    imei_map = {}

    async for message in queue:
        with message.process():
            logger.info(message.body)
            data = json.loads(message.body)
            imei = None
            device_id = None
            if data.get("imei", None):
                if imei_map.get(data["imei"]):
                    device_id = imei_map.get(data["imei"])
                else:
                    device_id = await get_device_id(data["imei"])
                    if device_id:
                        imei_map[data["imei"]] = device_id
            elif data.get("device", None):
                device_id = data["device"]

            file_bytes = base64.b64decode(data.get("file_bytes"))
            file_name, file_bytes = file_agg.add_file_bytes(
                device_id,
                data.get("file_name"),
                data.get("num_packets"),
                data.get("packet_number"),
                file_bytes
            )
            logger.debug(file_agg)
            camera_number = data.get("camera_number", "0")
            camera_time = data.get("camera_time", str(datetime.datetime.utcnow()))
            log_time = data.get("log_time", str(datetime.datetime.utcnow()))

            if file_bytes:
                parts = file_name.split(b'_')
                if len(parts) > 0:
                    date_as_dt = meitrack_date_to_datetime(parts[0])
                    if date_as_dt is not None:
                        camera_time = date_as_dt
                logger.debug(log_time)
                logger.log(
                    13,
                    "We have a full file %s, %s, %s, %s, %s, %s",
                    device_id,
                    camera_number,
                    camera_time,
                    file_bytes,
                    file_name,
                    log_time
                )
                result = add_camera_image(device_id, camera_number, camera_time, file_bytes, file_name, log_time)
                logger.info("Added file {} to geotool with result {}".format(file_name, result))