
import logging
from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError
from sim_chat_lib.exception import LoginError
from .encapsulation import command_as_json, calc_hash

logger = logging.getLogger(__name__)


class ChatClient(BaseChatClient):
    def __init__(self, sock_fd, imei, version, proto_version, device_name, seed, login_hash):
        super(ChatClient, self).__init__(sock_fd)
        self.imei = imei
        self.version = version
        self.proto_version = 2
        self.device_name = device_name
        self.seed = seed
        self.login_hash = login_hash
        self.check_login()

    def check_login(self):
        real_hash = calc_hash(
            "KernelRelease", self.seed, self.imei, self.version, self.proto_version, self.device_name
        )
        if real_hash != self.login_hash:
            raise LoginError("Invalid login hash")

    def send_command(self, command):
        type_arr = command.split(',', 1)
        if len(type_arr) == 2:
            if type_arr[0] == "cli":
                self.send_cli(type_arr[1])
            if type_arr[0] == "sio":
                self.send_sio(type_arr[1])

    def send_sio(self, command):
        send_buffer = command_as_json("command", command, "Please press enter:", seed=self.seed)
        self.send_data(send_buffer)

    def send_cli(self, command):
        send_buffer = command_as_json("cli", command, "Please press enter:", seed=self.seed)
        self.send_data(send_buffer)

    def send_data(self, data):
        return super(ChatClient, self).send_data(data)

    def receive_data(self):
        return super(ChatClient, self).receive_data()

    def get_client_details(self):
        start = super(ChatClient, self).get_client_details()
        return "ident: %s, imei: %s, version: %s, proto_version: %s, device_name %s, seed: %s, remote: %s, age: %s" % (
            self.ident(), self.imei, self.version, self.proto_version, self.device_name, self.seed, start, self.age()
        )

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