import os
import pika
import logging
import json

logger = logging.getLogger(__name__)

MESSAGE_QUEUE_CONXN = None
MESSAGE_QUEUE_CHANNEL = None


def open_message_queue_conxn():
    global MESSAGE_QUEUE_CONXN
    global MESSAGE_QUEUE_CHANNEL
    message_queue_host = os.environ.get("MQ_HOST", 'localhost')
    MESSAGE_QUEUE_CONXN = pika.BlockingConnection(pika.ConnectionParameters(host=message_queue_host))
    MESSAGE_QUEUE_CHANNEL = MESSAGE_QUEUE_CONXN.channel()
    # self.channel.exchange_declare(exchange='logs',
    #                          exchange_type='fanout')
    MESSAGE_QUEUE_CHANNEL.queue_declare(queue='firmware_update')
    MESSAGE_QUEUE_CHANNEL.queue_declare(queue='cell_update')
    MESSAGE_QUEUE_CHANNEL.queue_declare(queue='gps_update')
    MESSAGE_QUEUE_CHANNEL.queue_declare(queue='event_log')


def publish_to_mq(routing_key, data):
    global MESSAGE_QUEUE_CONXN
    global MESSAGE_QUEUE_CHANNEL
    if not MESSAGE_QUEUE_CONXN:
        return False
    try:
        if MESSAGE_QUEUE_CONXN.is_open:
            open_message_queue_conxn()
        add_result_ok = MESSAGE_QUEUE_CHANNEL.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=json.dumps(data, ensure_ascii=False),
        )
        return add_result_ok
    except pika.exceptions.AMQPError as err:
        logger.error("Unable to add message to queue. Error: %s", err)
        if MESSAGE_QUEUE_CONXN.is_open:
            MESSAGE_QUEUE_CONXN.close()
    except TypeError as err:
        logger.error("TypeError: Unable to convert json for publishing to message queue. Data is %s", data)
    except ValueError as err:
        logger.error("ValueError: Unable to convert json for publishing to message queue. Data is %s", data)
    return False
