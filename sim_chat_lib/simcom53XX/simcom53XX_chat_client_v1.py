
import logging
import binascii
from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError, ProtocolError
from sim_chat_lib.simcom53XX.encapsulation import command_as_json
from sim_chat_lib.simcom53XX import aes

logger = logging.getLogger(__name__)


class ChatClient(BaseChatClient):
    def __init__(self, sock_fd, report_queue, imei, version):
        super(ChatClient, self).__init__(sock_fd, report_queue)
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

    def get_client_details(self):
        start = super(ChatClient, self).get_client_details()
        return "simcom53XX, ident: %s, imei: %s, version: %s, remote: %s, age: %s" % (
            self.ident(), self.imei, self.version, start, self.age()
        )

    def ident(self):
        return "imei-%s" % (self.imei,)

    def process_data(self, data):
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
        super().process_data(data)
        try:
            byte_converter = lambda x: x.encode()
            if isinstance(data, str):
                byte_converter = lambda x: x

            super(ChatClient, self).update_last_tick()
            logger.log(13, data[0:6])
            if data[0:6] == byte_converter("C0NXN>"):
                logger.log(13,
                    "Received a heartbeat packet from %s with ident %s",
                    self.get_remote_ip(),
                    self.ident()
                )
            elif data[0:4] == byte_converter("MSG>"):
                logger.log(13,
                    "Received a message packet from %s with ident %s with data %s",
                    self.get_remote_ip(),
                    self.ident(),
                    data
                )
            elif data[0:3] == b"ENC":
                try:
                    logger.log(13, data)
                    counter = 0
                    logger.log(13, type(data))
                    delimiter = ord(b'>')
                    if isinstance(data, str):
                        delimiter = '>'
                    for i in range(0, 30):
                        if data[i] == delimiter:
                            counter = i
                            break
                    logger.log(13, "Counter is %s", counter)
                    counter = counter + 1
                    header = data[0:counter-1].decode()
                    logger.log(13, "Header is %s", header)
                    enc_data = data[counter:]
                    # header, enc_data = data.split('>', 1)
                    msg_type, msg_bytes = header.split(":", 1)
                    try:
                        msg_bytes_int = int(msg_bytes)
                    except ValueError as err:
                        raise ProtocolError("Unable to calculate encrypted message length")
                    logger.log(13, msg_bytes)
                    logger.log(13, len(enc_data))
                    logger.log(13, binascii.hexlify(enc_data))
                    if len(enc_data) == msg_bytes_int:
                        decrypted = aes.decrypt(enc_data)
                        logger.log(13, decrypted)
                        return decrypted
                except Exception as err:
                    raise ProtocolError("Error in decrypting data")
            else:
                logger.log(13, "%s", self.ident())
                logger.log(13, data)
                return "IMEI: %s\nDATA: %s" % (self.ident(), data)
        except Exception as err:
            raise ProtocolError("Unknown protocol error in process_data")

        return None

    def request_client_info(self):
        self.send_command("sio,ati")

    def request_client_location(self):
        self.send_command("sio,at+cgspinfo")

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
    globals()[socket.socket.getpeername] = lambda x: ("127.0.0.1", 123)
    doctest.testmod(
        extraglobs=
        {
            't': ChatClient(socket.socket(socket.AF_INET, socket.SOCK_STREAM), "imei", "base"),

        }
    )