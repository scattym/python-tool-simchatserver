import binascii
import logging

from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError
from sim_chat_lib.exception import LoginError, ProtocolError
from sim_chat_lib.meitrack import GPRSParseError
from sim_chat_lib.meitrack.error import GPRSError
from sim_chat_lib.meitrack.gprs_protocol import parse_data_payload
from sim_chat_lib.meitrack.build_message import stc_request_location_message

logger = logging.getLogger(__name__)


class MeitrackChatClient(BaseChatClient):
    def __init__(self, sock_fd, imei):
        super(MeitrackChatClient, self).__init__(sock_fd)
        self.imei = imei
        self.buffer = ''

    def check_login(self):
        return True

    def send_command(self, command):
        pass

    def get_client_details(self):
        start = super(MeitrackChatClient, self).get_client_details()
        return "type: meitrack, ident: %s, remote: %s, age: %s" % (
            self.ident(), start, self.age()
        )

    def ident(self):
        return "imei-%s" % (self.imei,)

    def process_data(self, data):
        super(MeitrackChatClient, self).update_last_tick()
        if len(self.buffer) <= 1024:
            try:
                self.buffer += data.decode()
            except UnicodeDecodeError as err:
                logger.error("Unable to convert bytes to string %s", data)
                raise ChatError("Unable to convert bytes to string")

        try:
            gprs_list, before, after = parse_data_payload(self.buffer)
        except GPRSParseError as err:
            logger.error("Parsing error on buffer %s", self.buffer)
            raise ProtocolError("Problem parsing meitrack buffer")

        return_str = "%s " % self.ident()
        for gprs in gprs_list:
            if not self.imei:
                self.imei = gprs.imei
            print(gprs)
            return_str += repr(gprs)

        self.buffer = after or ""
        return return_str

    def request_client_info(self):
        if not self.imei:
            logger.error("Unable to request location as client id not yet known")
        else:
            try:
                gprs = stc_request_location_message(self.imei)
                self.send_data(repr(gprs))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")
