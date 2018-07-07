import datetime
import logging
import socket
from sim_chat_lib.exception import ClientClosedError
from sim_chat_lib.report.async_api import queue_report, queue_config_request

logger = logging.getLogger(__name__)

RECV_BUFFER = 4096


class ChatClient(object):
    def __init__(self, sock_fd, report_queue):
        self.sock_fd = sock_fd
        self.report_queue = report_queue
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
        self.last_tick = datetime.datetime.now()

    def on_login(self):
        self.request_client_info()

    def send_data(self, data):
        try:
            data = data.encode()
        except AttributeError as err:
            logger.log(13, "Already encoded")
        # logger.info("Sending data to {}. Data: {}".format(self.ident(), data))
        logger.info("Tx {}. Data: {}".format(self.ident(), data))
        try:
            self.sock_fd.send(data)
        except socket.error as err:
            logger.error("We tried to write to the socket but got error: %s", err)
        except socket.timeout as err:
            logger.error("We tried to write to the socket but got timeout error: %s", err)

        self.update_last_tick()

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
        logger.info("Rx {}. Data: {}".format(self.ident(), data))
        self.update_last_tick()
        if data:
            return self.process_data(data)
        else:
            self.on_client_close()
            raise ClientClosedError("No data on receive. Client went away.")

    def get_remote_ip(self):
        return "%s:%s" % (self.ip_address, self.port)

    def get_client_details(self):
        return self.get_remote_ip()

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
        now = datetime.datetime.now()
        return now - last_tick

    def has_expired(self):
        if self.age > 300:
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

    def queue_report(self, report):
        return queue_report(report, self.report_queue)

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

    def set_heartbeat_interval(self, seconds):
        logger.log(13, "Setting heartbeat not implemented for this device.")

    def request_firmware_update(self):
        logger.log(13, "Updating firmware not implemented for this device.")

    def request_cancel_firmware_update(self):
        logger.log(13, "Updating firmware not implemented for this device.")

    def update_configuration(self):
        pass

    def parse_config(self, response):
        pass

    def parse_firmware_version(self, response):
        pass

    def parse_firmware_binary(self, response):
        pass
