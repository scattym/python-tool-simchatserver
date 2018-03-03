
import logging
import binascii
from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError
from .encapsulation import command_as_json
from . import aes

logger = logging.getLogger(__name__)


class ChatClient(BaseChatClient):
    def __init__(self, sock_fd, imei, version):
        super(ChatClient, self).__init__(sock_fd)
        self.imei = imei
        self.version = version

    def send_command(self, command):
        type_arr = command.split(',', 1)
        if len(type_arr) == 2:
            if type_arr[0] == "cli":
                self.send_cli(type_arr[1])
            if type_arr[0] == "sio":
                self.send_sio(type_arr[1])

    def send_cli(self, command):
        send_buffer = command_as_json("cli", command, "Please press enter:")
        self.send_data(send_buffer)

    def send_sio(self, command):
        send_buffer = command_as_json("command", command, "Please press enter:")
        self.send_data(send_buffer)


    def send_data(self, data):
        return super(ChatClient, self).send_data(data)

    def receive_data(self):
        payload = super(ChatClient, self).receive_data()
        # if payload:
        #     logger.debug(payload)
        #     if payload[0:3] == "ENC":
        #
        #         header, data = payload.split('>', 1)
        #         msg_type, msg_bytes = header.split(":", 1)
        #         logger.debug(msg_bytes)
        #         if len(data) == msg_bytes:
        #             decrypted = decrypt(data)
        #             logger.debug(decrypted)
        #             return decrypted
        # logger.debug("Clear message")
        return payload

    def get_client_details(self):
        start = super(ChatClient, self).get_client_details()
        return "ident: %s, imei: %s, version: %s, remote: %s, age: %s" % (
            self.ident(), self.imei, self.version, start, self.age()
        )

    def ident(self):
        return "imei-%s" % (self.imei,)

    def process_data(self, data):
        super(ChatClient, self).update_last_tick()
        logger.debug(data[0:6])
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
        elif data[0:3] == "ENC":
            logger.debug(data)
            header, enc_data = data.split('>', 1)
            msg_type, msg_bytes = header.split(":", 1)
            msg_bytes_int = int(msg_bytes)
            logger.debug(msg_bytes)
            logger.debug(len(enc_data))
            logger.debug(binascii.hexlify(enc_data))
            if len(enc_data) == msg_bytes_int:
                decrypted = aes.decrypt(enc_data)
                logger.debug(decrypted)
                return decrypted
        else:
            logger.debug("%s", self.ident())
            logger.debug(data)
            return "IMEI: %s\nDATA: %s" % (self.ident(), data)