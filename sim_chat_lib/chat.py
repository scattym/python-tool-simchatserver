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
        self.ip_address = peer[0]
        self.port = peer[1]
        self.last_tick = datetime.datetime.now()

    def on_login(self):
        self.request_client_info()
        logger.error("On login not implemented in base class")

    def send_data(self, data):
        try:
            data = data.encode()
        except AttributeError as err:
            logger.debug("Already encoded")
        logger.debug("Sending data to {}. Data: {}".format(self.ident(), data))
        self.sock_fd.send(data)
        self.update_last_tick()

    def receive_data(self):
        data = self.sock_fd.recv(RECV_BUFFER)
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
        logger.debug("Client closed connection: %s", self.ident())

    def queue_config_request(self, config_request):
        logger.debug("Queue config request start")
        result = queue_config_request(config_request, self.report_queue)
        logger.debug("Queue config request finished")

    def queue_report(self, report):
        return queue_report(report, self.report_queue)

    def __str__(self):
        return self.get_client_details()

    def reboot(self):
        logger.debug("Reboot not implemented on this device.")

    def request_client_location(self):
        logger.debug("Current location not implemented on this device.")

    def request_client_info(self):
        logger.debug("Client info not implemented for this device.")

    def request_client_photo_list(self):
        logger.debug("Client photo list not implemented for this device.")

    def request_client_take_photo(self, camera_number, file_name):
        logger.debug("Client photo list not implemented for this device.")

    def set_heartbeat_interval(self, seconds):
        logger.debug("Setting heartbeat not implemented for this device.")
