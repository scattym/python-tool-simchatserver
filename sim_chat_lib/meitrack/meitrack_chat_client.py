import binascii
import logging

from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError
from sim_chat_lib.exception import LoginError, ProtocolError
from sim_chat_lib.meitrack import GPRSParseError
from sim_chat_lib.meitrack.error import GPRSError
from sim_chat_lib.meitrack.gprs_protocol import parse_data_payload
from sim_chat_lib.meitrack.build_message import stc_request_location_message, stc_request_device_info
from sim_chat_lib.meitrack.gprs_to_report import gprs_to_report
import traceback

logger = logging.getLogger(__name__)


class MeitrackChatClient(BaseChatClient):
    def __init__(self, sock_fd, report_queue, imei):
        super(MeitrackChatClient, self).__init__(sock_fd, report_queue)
        self.imei = imei
        self.buffer = b''
        if imei:
            super(MeitrackChatClient, self).on_login()

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
                self.buffer += data
            except UnicodeDecodeError as err:
                logger.error("Unable to convert bytes to string %s", data)
                raise ChatError("Unable to convert bytes to string")

        try:
            gprs_list, before, after = parse_data_payload(self.buffer.decode())
        except UnicodeDecodeError as err:
            logger.error("Unicode decode error on buffer %s", self.buffer)
            logger.debug(traceback.print_exc())
            raise ProtocolError("Problem parsing meitrack buffer, unable to decode buffer")
        except GPRSParseError as err:
            logger.error("Parsing error on buffer %s", self.buffer)
            logger.debug(traceback.print_exc())
            raise ProtocolError("Problem parsing meitrack buffer")

        return_str = "%s " % self.ident()
        for gprs in gprs_list:
            if not self.imei:
                self.imei = gprs.imei
            print(gprs)
            report = gprs_to_report(gprs)
            queue_result = self.queue_report(report)
            if not queue_result:
                logger.error("Unable to add record to queue: %s", repr(gprs))
            return_str += repr(gprs)

        logger.debug("Leftover bytes count %s, with data: %s", len(after), after)
        self.buffer = (after or "").encode()
        return return_str

    def request_location(self):
        if not self.imei:
            logger.error("Unable to request location as client id not yet known")
        else:
            try:
                gprs = stc_request_location_message(self.imei)
                self.send_data(repr(gprs))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")

    def request_client_info(self):
        if not self.imei:
            logger.error("Unable to request client info as client id not yet known")
        else:
            try:
                gprs = stc_request_device_info(self.imei)
                logger.debug(gprs)
                logger.debug(repr(gprs))
                self.send_data(repr(gprs))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")
