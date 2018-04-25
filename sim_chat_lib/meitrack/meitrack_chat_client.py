import binascii
import logging

from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError
from sim_chat_lib.exception import LoginError, ProtocolError
from sim_chat_lib.meitrack import GPRSParseError
from sim_chat_lib.meitrack.error import GPRSError
from sim_chat_lib.meitrack.gprs_protocol import parse_data_payload
from sim_chat_lib.meitrack import build_message
from sim_chat_lib.meitrack.gprs_to_report import gprs_to_report, file_download_to_report
from sim_chat_lib.report import MeitrackConfigRequest
import traceback

logger = logging.getLogger(__name__)


class FileDownload(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.expecting_packets = None
        self.packets = {}

    def add_packet(self, gprs_packet):
        if gprs_packet and gprs_packet.enclosed_data:
            file_name, num_packets, packet_number, file_bytes = gprs_packet.enclosed_data.get_file_data()
            if file_name == self.file_name:
                if not self.expecting_packets:
                    self.expecting_packets = int(num_packets.decode())
                logger.debug("Adding packet %s to file %s", packet_number, self.file_name)
                packet_number_int = int(packet_number.decode())
                self.packets[packet_number_int] = file_bytes

    def is_complete(self):
        if not self.expecting_packets:
            return False
        for i in range(1, self.expecting_packets+1):
            if i not in self.packets:
                logger.debug("File is not yet complete. Missing %s from %s", i, self.expecting_packets)
                return False
        logger.debug("File is complete")
        return True

    def fragment_list_as_string(self):
        return_str = ""
        for i in self.packets:
            return_str += "{} ".format(i)
        return return_str

    def return_file_contents(self):
        if not self.is_complete():
            logger.debug("File is not complete yet. Returning None")
            return None
        else:
            file_bytes = b""
            for i in range(1, self.expecting_packets+1):
                file_bytes = file_bytes + self.packets[i]
            return file_bytes


class MeitrackChatClient(BaseChatClient):
    def __init__(self, sock_fd, report_queue, imei):
        super(MeitrackChatClient, self).__init__(sock_fd, report_queue)
        self.imei = imei
        self.buffer = b''
        if imei:
            self.on_login()
        self.file_list = []
        self.file_download_list = []

    def check_login(self):
        return True

    def send_command(self, command):
        pass

    def get_client_details(self):
        start = super(MeitrackChatClient, self).get_client_details()
        return "type: meitrack, ident: %s, remote: %s, age: %s" % (
            self.ident(), start, self.age()
        ) + self.get_download_details()

    def get_download_details(self):
        if self.file_download_list:
            return_str = "File Downloads\n"
            for file_download in self.file_download_list:
                return_str += "{}, {}, {}".format(
                    file_download.file_name,
                    file_download.expecting_packets,
                    file_download.fragment_list_as_string()
                )

    def ident(self):
        return "imei-%s" % (self.imei.decode())

    def on_login(self):
        super(MeitrackChatClient, self).on_login()
        config_request = MeitrackConfigRequest()
        config_request.imei = self.imei
        logger.debug("Add config request to queue %s", config_request)
        self.queue_config_request(config_request)
        logger.debug("end of on login")

    def parse_config(self, response):
        logger.info("Parsing config response %s", response)
        if not response:
            logger.error("No response to parse.")
            return
        if response.get("heartbeat_interval"):
            gprs = build_message.stc_set_heartbeat_interval(self.imei, response.get("heartbeat_interval"))
            self.send_data(gprs.as_bytes())
        if response.get("time_interval"):
            gprs = build_message.stc_set_tracking_by_time_interval(self.imei, response.get("heartbeat_interval"))
            self.send_data(gprs.as_bytes())
        if response.get("cornering_angle"):
            gprs = build_message.stc_set_cornering_angle(self.imei, response.get("cornering_angle"))
            self.send_data(gprs.as_bytes())
        if response.get("tracking_by_distance"):
            gprs = build_message.stc_set_tracking_by_distance(self.imei, response.get("tracking_by_distance"))
            self.send_data(gprs.as_bytes())

    def process_data(self, data):
        super(MeitrackChatClient, self).update_last_tick()
        if len(self.buffer) <= 2048:
            try:
                self.buffer += data
            except UnicodeDecodeError as err:
                logger.error("Unable to convert bytes to string %s", data)
                raise ChatError("Unable to convert bytes to string")
        else:
            raise ChatError("Buffer too long")

        try:
            gprs_list, before, after = parse_data_payload(self.buffer)
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
                logger.error("Unable to add record to queue: %s", (gprs.as_bytes()))
            try:
                return_str += (gprs.as_bytes()).decode()
            except UnicodeDecodeError as err:
                logger.error("Unable to decode response to send to masters")
                return_str += "Binary data"

            if gprs and gprs.enclosed_data:
                file_name, num_packets, packet_number, file_bytes = gprs.enclosed_data.get_file_data()
                return_str += "File: %s, packet: %s, of: %s" % (
                    file_name.decode(),
                    packet_number.decode(),
                    num_packets.decode()
                )
                if file_name and file_bytes:
                    found = False
                    for file_download in self.file_download_list:
                        if file_download.file_name == file_name:
                            found = True
                            file_download.add_packet(gprs)
                            if file_download.is_complete():
                                report = file_download_to_report(self.imei.decode(), file_download)
                                self.queue_report(report)
                                self.file_download_list.remove(file_download)

                    if not found:
                        file_download = FileDownload(file_name)
                        file_download.add_packet(gprs)
                        self.file_download_list.append(file_download)
                    if file_name:
                        os_file_name = "/tmp/%s" % file_name.decode()
                        logger.debug("Writing to file %s", os_file_name)
                        file = open(os_file_name, 'ab')
                        file.write(file_bytes)
                        file.close()

        logger.debug("Leftover bytes count %s, with data: %s", len(after), after)
        self.buffer = (after or "").encode()
        return return_str

    def request_client_location(self):
        if not self.imei:
            logger.error("Unable to request location as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_location_message(self.imei)
                self.send_data((gprs.as_bytes()))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")

    def request_client_info(self):
        if not self.imei:
            logger.error("Unable to request client info as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_device_info(self.imei)
                logger.debug(gprs)
                logger.debug(gprs.as_bytes())
                self.send_data((gprs.as_bytes()))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")

    def request_client_photo_list(self):
        if not self.imei:
            logger.error("Unable to request photo list as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_photo_list(self.imei)
                self.send_data((gprs.as_bytes()))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")

    def request_client_take_photo(self, camera_number, file_name=None):
        if not self.imei:
            logger.error("Unable to request client to take a photo as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_take_photo(self.imei, camera_number, file_name)
                self.send_data((gprs.as_bytes()))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")

    def request_get_file(self, file_name, payload_start_index=0):
        if not self.imei:
            logger.error("Unable to request client to take a photo as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_get_file(self.imei, file_name, payload_start_index)
                self.send_data((gprs.as_bytes()))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")