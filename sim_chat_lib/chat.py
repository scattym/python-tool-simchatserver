import datetime
import logging
import socket
from sim_chat_lib.exception import ClientClosedError

logger = logging.getLogger(__name__)

RECV_BUFFER = 4096


class ChatClient(object):
    def __init__(self, sock_fd):
        self.sock_fd = sock_fd
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

    def send_data(self, data):
        self.sock_fd.send(data.encode())

    def receive_data(self):
        data = self.sock_fd.recv(RECV_BUFFER)
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

    def __str__(self):
        return self.get_client_details()