import binascii
import logging

from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError
from sim_chat_lib.exception import LoginError, ProtocolError
from sim_chat_lib.simcom53XX.encapsulation import command_as_json, calc_hash
from sim_chat_lib.simcom53XX import aes

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
            raise LoginError("Invalid login hash. Should be: %s, but was %s" % (real_hash, self.login_hash))

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
        """
        Function to process data after received from socket

        :param data:
        :return:

        >>> t.process_data("MSG>test") is None
        True
        >>> t.process_data("C0NXN>test") is None
        True
        >>> t.process_data("DATA>blah\\n")
        'IMEI: imei-imei\\nDATA: DATA>blah\\n'
        >>> t.process_data("DATA>blah")
        'IMEI: imei-imei\\nDATA: DATA>blah'
        >>> t.process_data(b"ENCDATA:48>" + ENC_DATA_BYTES)
        'This is a test string for encryption'
        """
        try:
            byte_converter = lambda x: x.encode()
            if isinstance(data, str):
                byte_converter = lambda x: x

            super(ChatClient, self).update_last_tick()
            logger.debug(data[0:6])
            if data[0:6] == byte_converter("C0NXN>"):
                logger.debug(
                    "Received a heartbeat packet from %s with ident %s",
                    self.get_remote_ip(),
                    self.ident()
                )
            elif data[0:4] == byte_converter("MSG>"):
                logger.debug(
                    "Received a message packet from %s with ident %s with data %s",
                    self.get_remote_ip(),
                    self.ident(),
                    data
                )
            elif data[0:3] == b"ENC":
                try:
                    logger.debug(data)
                    counter = 0
                    logger.debug(type(data))
                    delimiter = ord(b'>')
                    if isinstance(data, str):
                        delimiter = '>'
                    for i in range(0, 30):
                        if data[i] == delimiter:
                            counter = i
                            break
                    logger.debug("Counter is %s", counter)
                    counter = counter + 1
                    header = data[0:counter-1].decode()
                    logger.debug("Header is %s", header)
                    enc_data = data[counter:]
                    # header, enc_data = data.split('>', 1)
                    msg_type, msg_bytes = header.split(":", 1)
                    try:
                        msg_bytes_int = int(msg_bytes)
                    except ValueError as err:
                        raise ProtocolError("Unable to calculate encrypted message length")
                    logger.debug(msg_bytes)
                    logger.debug(len(enc_data))
                    logger.debug(binascii.hexlify(enc_data))
                    if len(enc_data) == msg_bytes_int:
                        decrypted = aes.decrypt(enc_data)
                        logger.debug(decrypted)
                        return decrypted
                except Exception as err:
                    raise ProtocolError("Error in decrypting data")
            else:
                logger.debug("%s", self.ident())
                logger.debug(data)
                return "IMEI: %s\nDATA: %s" % (self.ident(), data)
        except Exception as err:
            raise ProtocolError("Unknown protocol error in process_data")

        return None

if __name__ == "__main__":
    import doctest
    import socket
    import binascii
    from sim_chat_lib import chat
    ENC_DATA_BYTES = binascii.unhexlify(
        "acb72514a79fe2400222cd7e01386649d693345ac17fa95017a94b1dae4769dd0d8ad5b3c81352423bb1a839cf426a85"
    )
    ENC_DATA_STR = binascii.unhexlify(
        "acb72514a79fe2400222cd7e01386649d693345ac17fa95017a94b1dae4769dd0d8ad5b3c81352423bb1a839cf426a85"
    )
    doctest.testmod(
        extraglobs=
        {
            't': ChatClient(socket.socket(socket.AF_INET, socket.SOCK_STREAM), "imei", "base", "2", "5360", "seed", "7031577d53c0248bb4cb6f93d980963e17ad12e794c925b35bc8e036ae325a86"),

        }
    )