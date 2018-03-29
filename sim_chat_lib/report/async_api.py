import datetime
import multiprocessing
import logging
from queue import Queue

from sim_chat_lib.geotool_api import device_api

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
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                # print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                break
            # print '%s: %s' % (proc_name, next_task)
            answer = next_task()
            self.task_queue.task_done()
            if self.result_queue:
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
                    None,
                    None,
                    None,
                    None,
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

        return self.result

    def __str__(self):
        return '%s -> %s' % (self.report.imei, self.result)


def queue_report(report, task_queue, blocking=False, timeout=1):
    try:
        task_queue.put(Task(report), blocking, timeout)
        return True
    except Queue.Full as err:
        logger.error("Task queue is full. Not adding item.")
        return False

        
def start_consumers(num_consumers=10, queue_depth=1000, bin_results=True):
    tasks = multiprocessing.JoinableQueue(queue_depth)
    results = None
    alarm_size = (queue_depth * 0.75)
    if not bin_results:
        results = multiprocessing.Queue()

    # Start consumers
    num_consumers = int(num_consumers)
    logger.debug('Creating %d consumers' % num_consumers)
    consumers = [Consumer(tasks, results, alarm_size) for i in range(num_consumers)]

    for w in consumers:
        w.start()

    return tasks, results


def stop_consumers(task_queue, wait_for_finish=True, num_consumers=10):

    # Add a poison pill for each consumer
    for i in range(num_consumers):
        task_queue.put(None)

    if wait_for_finish:
        # Wait for all of the tasks to finish
        task_queue.join()
