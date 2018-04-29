import base64

import datetime
import multiprocessing
import logging
from queue import Queue

from sim_chat_lib import geotool_api
from sim_chat_lib.geotool_api import device_api
from sim_chat_lib.geotool_api import meitrack_config_api

logger = logging.getLogger(__name__)


class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue, alarm_size):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.alarm_size = alarm_size

    def run(self):
        proc_name = self.name
        while True:
            logger.debug("Asking for next item")
            next_task = self.task_queue.get()
            logger.debug("Got a new task %s", next_task)
            if next_task is None:
                # Poison pill means shutdown
                # print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                break
            # print '%s: %s' % (proc_name, next_task)
            answer = next_task()
            logger
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

    def __call__(self):
        log_time = datetime.datetime.now()
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
                    log_time
                )
            except Exception as err:
                logger.error("Exception in async task, logging gps entry %s", err)
        if self.report.battery_level and self.report.battery_voltage and self.report.mnc:
            try:
                self.result1 = device_api.cell_update(
                    self.report.imei,
                    self.report.battery_level,
                    self.report.battery_voltage,
                    self.report.mcc,
                    self.report.mnc,
                    self.report.lac,
                    self.report.ci,
                    self.report.rx_level,
                    self.report.timestamp,
                    log_time
                )
            except Exception as err:
                logger.error("Exception in async task, logging gps entry %s", err)

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
                            self.report.event_type
                    )
            except Exception as err:
                logger.error("Exception in async task, logging file entry %s", err)

        return self.result

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

    def __str__(self):
        return '%s -> %s' % (self.config_request.imei, self.result)


def queue_report(report, task_queue, blocking=False, timeout=1):
    try:
        task_queue.put(Task(report), blocking, timeout)
        return True
    except Queue.Full as err:
        logger.error("Task queue is full. Not adding item.")
        return False


def queue_config_request(config_request, task_queue, blocking=False, timeout=1):

    try:
        logger.debug("Adding config request to queue")
        task_queue.put(MeitrackConfigRequestTask(config_request), blocking, timeout)
        logger.debug("Added config request to queue")
        return True
    except Queue.Full as err:
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
