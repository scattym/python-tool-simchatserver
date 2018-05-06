import json
import datetime
import multiprocessing
import logging
import queue
import traceback
import pika
import os

from sim_chat_lib import geotool_api
from sim_chat_lib.geotool_api import device_api, driver_api
from sim_chat_lib.geotool_api import meitrack_config_api

logger = logging.getLogger(__name__)
MQ_HOST = os.environ.get("MQ_HOST")


class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue, alarm_size):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.alarm_size = alarm_size
        self.mq_conxn = None
        self.connection = None
        self.channel = None
        if MQ_HOST:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            self.channel = self.connection.channel()
            # self.channel.exchange_declare(exchange='logs',
            #                          exchange_type='fanout')
            self.channel.queue_declare(queue='firmware_update')
            self.channel.queue_declare(queue='cell_update')
            self.channel.queue_declare(queue='gps_update')
            # logger.debug("Starting publisher")
            # self.mq_conxn = ExamplePublisher(
            #     'amqp://guest:guest@localhost:5672/%2F?connection_attempts=3&heartbeat_interval=3600'
            # )
            # Thread(target=self.mq_conxn.run).start()

    def run(self):
        proc_name = self.name
        while True:
            logger.debug("Asking for next item")
            next_task = self.task_queue.get()

            if next_task is None:
                # Poison pill means shutdown
                # print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                break

            if self.mq_conxn:
                logger.debug("Adding message to message queue")
                # answer = self.channel.publish_message(next_task)
                message_list = next_task.as_json()
                if message_list:
                    for message in message_list:
                        add_result_ok = self.channel.basic_publish(
                            exchange='',
                            routing_key=message["key"],
                            body=json.dumps(message["data"], ensure_ascii=False),
                        )
                        logger.debug("Add result was %s", add_result_ok)

            logger.debug("Got a new task %s", next_task)
            # print '%s: %s' % (proc_name, next_task)
            answer = next_task()

            self.task_queue.task_done()
            if self.result_queue and answer:
                self.result_queue.put(answer)
            try:
                if self.task_queue.qsize() > self.alarm_size:
                    logger.error("Queue depth is getting large. Value is %s", self.task_queue.qsize())
                logger.debug("Task queue depth is %s", self.task_queue.qsize())
            except NotImplementedError as err:
                logger.debug("Task queue depth not implemented on this platform")
        return


class Task(object):
    def __init__(self, report):
        self.report = report
        self.result = None
        self.log_time = datetime.datetime.now()

    def __call__(self):

        if self.report.imei and self.report.gps_latitude and self.report.gps_longitude:
            try:
                self.result = device_api.device_update_by_long_lat(
                    self.report.imei,
                    self.report.gps_longitude,
                    self.report.gps_latitude,
                    self.report.direction,
                    self.report.speed,
                    self.report.altitude,
                    self.report.horizontal_accuracy,
                    None,
                    self.report.num_sats,
                    self.report.timestamp,
                    self.log_time
                )
            except Exception as err:
                logger.error("Exception in async task, logging gps entry %s", err)
                logger.error(traceback.print_exc())

        if self.report.battery_level and self.report.battery_voltage and self.report.mnc:
            try:
                self.result = geotool_api.cell_update(
                    self.report.imei,
                    self.log_time,
                    self.report.ci,
                    self.report.lac,
                    self.report.mcc,
                    self.report.mnc,
                    self.report.rx_level,
                )
            except Exception as err:
                logger.error("Exception in async task, logging gps entry %s", err)
                logger.error(traceback.print_exc())

        if self.report.firmware_version and self.report.serial_number:
            try:

                self.result = device_api.device_parameters(
                    self.report.imei,
                    "meitrack",
                    "T333",
                    self.report.firmware_version,
                    self.report.serial_number,
                    self.report.firmware_version,
                )
            except Exception as err:
                logger.error("Exception in async task, logging file entry %s", err)
                logger.error(traceback.print_exc())

        if self.report.file_name is not None and self.report.file_data is not None:
            try:
                # image_base64 = base64.b64encode(self.report.)
                self.result = geotool_api.add_camera_image(
                    self.report.imei,
                    0,
                    self.report.timestamp,
                    self.report.file_data
                )
            except Exception as err:
                logger.error("Exception in async task, logging file entry %s", err)
                logger.error(traceback.print_exc())

        if self.report.event_type:
            try:
                if self.report.event_type == "SOS Button Pressed":
                    self.result = geotool_api.add_sos_event(self.report.imei, self.report.timestamp)
                else:
                    if self.report.event_type == "Engine On":
                        geotool_api.add_trip_log(self.report.imei, self.report.timestamp, "start")
                    elif self.report.event_type == "Engine Off":
                        geotool_api.add_trip_log(self.report.imei, self.report.timestamp, "stop")

                    self.result = geotool_api.add_event_log(
                        self.report.imei,
                        self.report.timestamp,
                        2,
                        self.report.event_type,
                        self.log_time,
                    )
            except Exception as err:
                logger.error("Exception in async task, logging file entry %s", err)
                logger.error(traceback.print_exc())

        if self.report.license_data is not None:
            try:
                self.result = driver_api.add_driver_log_by_payload(self.report.imei, self.report.license_data)
            except Exception as err:
                logger.error("Exception in async task, logging file entry %s", err)
                logger.debug(traceback.print_exc())

        return self.result

    def as_json(self):
        data = None
        data_list = []
        if self.report.firmware_version and self.report.serial_number:
            data = {
                "key": "firmware_update",
                "data": {
                    "log_time": str(self.log_time),
                    "imei": self.report.imei,
                    "manufacturer": "meitrack",
                    "model": "T333",
                    "revision": self.report.firmware_version,
                    "serial": self.report.serial_number,
                    "running_version": self.report.firmware_version,
                }
            }
            data_list.append(data)
            self.report.firmware_version = None
            self.report.serial_number = None

        if self.report.mnc:
            data = {
                "key": "cell_update",
                "data": {
                    "imei": self.report.imei,
                    "log_time": str(self.log_time),
                    "cell_id": self.report.ci,
                    "location_area_code": self.report.lac,
                    "mobile_country_code": self.report.mcc,
                    "mobile_network_code": self.report.mnc,
                    "primary_scrambling_code": None,
                    "secondary_sychronisation_code": None,
                    "rx_level": self.report.rx_level,
                }
            }
            data_list.append(data)
            self.report.mnc = None

        if self.report.imei and self.report.gps_latitude and self.report.gps_longitude:
            data = {
                "key": "gps_update",
                "data": {
                    "imei": self.report.imei,
                    "log_time": str(self.log_time),
                    "latitude": self.report.gps_latitude,
                    "longitude": self.report.gps_longitude,
                    "true_track": self.report.direction,
                    "mag_track": None,
                    "ground_speed": self.report.speed,
                    "altitude": self.report.altitude,
                    "timestamp": str(self.report.timestamp),
                    "dilution": self.report.horizontal_accuracy,
                    "num_sats": self.report.num_sats,
                }
            }
            data_list.append(data)
            self.report.gps_latitude = None
            self.report.gps_longitude = None

        return data_list

    def __str__(self):
        return '%s -> %s' % (self.report.imei, self.result)


class MeitrackConfigRequestTask(object):
    def __init__(self, config_request):
        logger.debug("init of meitrack config request")
        self.config_request = config_request
        self.result = None

    def __call__(self):
        try:
            imei = self.config_request.imei.decode()
        except AttributeError as err:
            logger.error("Unable to decode imei")
            imei = self.config_request.imei
        logger.debug("Calling config request for imei %s", imei)

        if imei:
            try:
                device_pk = device_api.get_device_pk(imei)
                config = meitrack_config_api.get_device_config(device_pk)
                self.result = {
                    "type": "config",
                    "imei": imei,
                    "response": config,
                }
            except Exception as err:
                logger.error("Exception in async task, logging gps entry %s", err)

        return self.result

    def as_json(self):
        return None

    def __str__(self):
        return '%s -> %s' % (self.config_request.imei, self.result)


def queue_report(report, task_queue, blocking=False, timeout=1):
    try:
        task_queue.put(Task(report), blocking, timeout)
        return True
    except queue.Full as err:
        logger.error("Task queue is full. Not adding item.")
        return False


def queue_config_request(config_request, task_queue, blocking=False, timeout=1):

    try:
        logger.debug("Adding config request to queue")
        task_queue.put(MeitrackConfigRequestTask(config_request), blocking, timeout)
        logger.debug("Added config request to queue")
        return True
    except queue.Full as err:
        logger.error("Task queue is full. Not adding item.")
        return False

        
def start_consumers(num_consumers=10, queue_depth=1000, bin_results=True):
    tasks = multiprocessing.JoinableQueue(queue_depth)
    results = None
    alarm_size = (queue_depth * 0.75)
    if not bin_results:
        results = multiprocessing.Queue(queue_depth)

    # Start consumers
    num_consumers = int(num_consumers)
    logger.debug('Creating %d consumers' % num_consumers)
    consumers = [Consumer(tasks, results, alarm_size) for i in range(num_consumers)]

    for w in consumers:
        w.start()

    return tasks, results


def get_result(result_queue, blocking=False, timeout=1):
    logger.debug("Getting response from result queue")
    if result_queue:
        result = result_queue.get(block=blocking, timeout=timeout)
        return result
    return None


def stop_consumers(task_queue, wait_for_finish=True, num_consumers=10):

    # Add a poison pill for each consumer
    for i in range(num_consumers):
        task_queue.put(None)

    if wait_for_finish:
        # Wait for all of the tasks to finish
        task_queue.join()
