import datetime
import logging
import socket
from sim_chat_lib.exception import ClientClosedError
from sim_chat_lib.report import event_to_report, DebugLogReport, DEBUG_LOG_DIRECTION_SERVER_TO_CLIENT, \
    DEBUG_LOG_DIRECTION_CLIENT_TO_SERVER
from sim_chat_lib.report.async_api import queue_report, queue_config_request

logger = logging.getLogger(__name__)

RECV_BUFFER = 4096


class ChatClient(object):
    def __init__(self, sock_fd, report_queue):
        self.sock_fd = sock_fd
        self.report_queue = report_queue
        self.debug = False
        self.imei = None
        try:
            peer = sock_fd.getpeername()
        except OSError as err:
            logger.error("Unable to get client details from socket: %s", err)
            peer = ("none", -1)
        except socket.error as err:
            logger.error("Unable to get client details from socket: %s", err)
            peer = ("none", -1)
        self.ip_address = peer[0]
        self.port = peer[1]
        self.last_tick = datetime.datetime.utcnow()
        self.print_comms = True

    def on_login(self):
        self.request_client_info()

    def send_data(self, data):
        try:
            data = data.encode()
        except AttributeError as err:
            logger.log(13, "Already encoded")
        # logger.info("Sending data to {}. Data: {}".format(self.ident(), data))
        logger.info("Tx {}, Data: {}".format(self.ident(), data))
        if self.print_comms:
            print("{}, Tx {}, Data: {}".format(datetime.datetime.utcnow(), self.ident(), data))
        if self.debug and self.imei is not None:
            self.queue_debug_log(data, DEBUG_LOG_DIRECTION_SERVER_TO_CLIENT)

        try:
            self.sock_fd.send(data)
        except socket.error as err:
            logger.error("We tried to write to the socket but got error: %s", err)
        except socket.timeout as err:
            logger.error("We tried to write to the socket but got timeout error: %s", err)
        # we don't want to update last tick as sending data
        # results in the connection never aging out.
        # self.update_last_tick()

    def receive_data(self):
        # TODO: Got a timeout here. Need to work out why this
        # is a blocking read. Should be set to non-blocking
        # after identified as a meitrack client. May not be happening
        # in the exception handling?
        data = None
        try:
            data = self.sock_fd.recv(RECV_BUFFER)
        except socket.error as err:
            logger.error("We tried to read from the socket but got error: %s", err)
        except socket.timeout as err:
            logger.error("We tried to read from the socket but got timeout error: %s", err)
        logger.info("Rx {}, Data: {}".format(self.ident(), data))
        if self.print_comms:
            print("{}, Rx {}, Data: {}".format(datetime.datetime.utcnow(), self.ident(), data))
        if self.debug and self.imei is not None:
            self.queue_debug_log(data, DEBUG_LOG_DIRECTION_CLIENT_TO_SERVER)
        self.update_last_tick()
        if data:
            return self.process_data(data)
        else:
            self.on_client_close()
            raise ClientClosedError("No data on receive. Client went away.")

    def get_remote_ip(self):
        return "%s:%s" % (self.ip_address, self.port)

    def get_client_details(self):
        return "IP: {}, DEBUG: {}".format(self.get_remote_ip(), self.debug)

    def ident(self):
        return None

    def check_for_timeout(self, date_dt):
        return None

    def process_data(self, data):
        return "Base client cannot parse data"

    def process_response_data(self, data):
        logger.error("Unable to process response in base class. Response is %s", data)

    def update_last_tick(self):
        self.last_tick = datetime.datetime.utcnow()

    def age(self):
        last_tick = self.last_tick
        logger.debug("Last tick is %s", last_tick)
        now = datetime.datetime.utcnow()
        logger.debug("Now is %s", last_tick)
        return (now - last_tick).total_seconds()

    def has_expired(self):
        if self.age() > 600:
            return True
        return False

    def on_client_close(self):
        logger.log(13, "Client closed connection: %s", self.ident())

    def on_server_close(self):
        logger.log(13, "Server closed connection: %s", self.ident())

    def queue_config_request(self, config_request):
        logger.log(13, "Queue config request start")
        result = queue_config_request(config_request, self.report_queue)
        logger.log(13, "Queue config request finished")

    def queue_debug_log(self, data, direction):
        report = DebugLogReport()
        report.imei = self.imei
        report.direction = direction
        report.data = data
        self.queue_report(report)

    def queue_report(self, report):
        return queue_report(report, self.report_queue)

    def queue_event_report(self, identifier, event_string):
        report = event_to_report(identifier, event_string)
        queue_result = self.queue_report(report)
        logger.log(13, "Queue add result was %s", queue_result)
        return queue_result

    def __str__(self):
        return self.get_client_details()

    def reboot(self):
        logger.log(13, "Reboot not implemented on this device.")

    def request_client_location(self):
        logger.log(13, "Current location not implemented on this device.")

    def request_client_info(self):
        logger.log(13, "Client info not implemented for this device.")

    def request_client_photo_list(self):
        logger.log(13, "Client photo list not implemented for this device.")

    def request_client_take_photo(self, camera_number, file_name):
        logger.log(13, "Client photo list not implemented for this device.")

    def request_get_file(self, file_name, payload_start_index=0):
        logger.log(13, "Client file retrieval not implemented for this device.")

    def request_delete_file(self, file_name):
        logger.log(13, "Client file deletion not implemented for this device.")

    def request_delete_all_files(self):
        logger.log(13, "Client all file delete not implemented for this device.")

    def set_heartbeat_interval(self, seconds):
        logger.log(13, "Setting heartbeat not implemented for this device.")

    def request_firmware_update(self):
        logger.log(13, "Updating firmware not implemented for this device.")

    def request_cancel_firmware_update(self):
        logger.log(13, "Updating firmware not implemented for this device.")

    def restart_device(self):
        logger.log(13, "Restarting device not implemented for this device.")

    def restart_gps(self):
        logger.log(13, "Restarting gps not implemented for this device.")

    def request_photo_event_flags(self):
        logger.log(13, "Request photo event flags not implemented for this device")

    def request_format_sdcard(self):
        logger.log(13, "Request photo event flags not implemented for this device")

    def set_output(self, pin, state):
        logger.log(13, "Set output not implemented for this device.")

    def update_configuration(self):
        pass

    def parse_config(self, response):
        pass

    def parse_firmware_version(self, response):
        pass

    def parse_firmware_binary(self, response):
        pass

    def set_snapshot_parameters(self, event_code=1, interval=20, count=1, upload=1, delete=1):
        pass
