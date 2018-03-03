
import logging
from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError
from encapsulation import command_as_json

logger = logging.getLogger(__name__)


class ChatClient(BaseChatClient):
    def __init__(self, sock_fd, imei, version):
        super(ChatClient, self).__init__(sock_fd)
        self.imei = imei
        self.version = version

    def send_command(self, command):
        send_buffer = command_as_json(command, "Please press enter:")
        self.send_data(send_buffer)

    def send_data(self, data):
        return super(ChatClient, self).send_data(data)

    def receive_data(self):
        return super(ChatClient, self).receive_data()

    def get_client_details(self):
        start = super(ChatClient, self).get_client_details()
        return "ident: %s, imei: %s, version: %s, remote: %s" % (self.ident(), self.imei, self.version, start)

    def ident(self):
        return "imei-%s" % (self.imei,)

    def process_data(self, data):
        super(ChatClient, self).update_last_tick()
        if data[0:6] == "C0NXN>":
            logger.debug(
                "Received a heartbeat packet from %s with ident %s",
                self.get_remote_ip(),
                self.ident()
            )
        elif data[0:4] == "MSG>":
            logger.debug(
                "Received a message packet from %s with ident %s",
                self.get_remote_ip(),
                self.ident()
            )
        else:
            logger.debug("%s: %s" % (self.ident(), data))
            return "IMEI: %s\nDATA: %s" % (self.ident(), data)