import base64

import datetime
import logging
import os
import traceback

from meitrack.build_message import stc_restart_gps, stc_restart_gsm
from meitrack.common import DIRECTION_CLIENT_TO_SERVER
from meitrack.file_list import FileListing, FileListingError
from meitrack.firmware_update import FirmwareUpdate, STAGE_FIRST, STAGE_SECOND, stc_cancel_ota_update
from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError
from sim_chat_lib.exception import ProtocolError
from meitrack.error import GPRSParseError
from meitrack.error import GPRSError
from meitrack.gprs_protocol import parse_data_payload
from meitrack import build_message, firmware_update
from sim_chat_lib.meitrack.gprs_to_report import gprs_to_report, get_firmware_binary_report, get_firmware_version_report
from sim_chat_lib.report import MeitrackConfigRequest


logger = logging.getLogger(__name__)

MT_PARTIAL_WAIT = int(os.environ.get("MT_PARTIAL_WAIT", "60"))
MT_PARTIAL_WAIT_DELTA = datetime.timedelta(seconds=MT_PARTIAL_WAIT)
MT_NEW_FILE_WAIT = int(os.environ.get("MT_NEW_FILE_WAIT", "480"))
MT_NEW_FILE_WAIT_DELTA = datetime.timedelta(seconds=MT_NEW_FILE_WAIT)
MT_FILE_LIST_WAIT = int(os.environ.get("MT_FILE_LIST_WAIT", "960"))
MT_FILE_LIST_WAIT_DELTA = datetime.timedelta(seconds=MT_FILE_LIST_WAIT)
EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
MT_UPDATE_HOST = os.environ.get("MT_UPDATE_HOST", "scs.pts.scattym.com")
MT_UPDATE_PORT = os.environ.get("MT_UPDATE_PORT", "65533")


def get_bytes_from_file(filename):
    return open(filename, "rb").read()


class MeitrackFirmwareClient(BaseChatClient):
    def __init__(self, sock_fd, report_queue, imei):
        super(MeitrackFirmwareClient, self).__init__(sock_fd, report_queue)
        self.message_counter = 0
        self.imei = imei
        self.buffer = b''
        self.current_download = None
        self.current_packet = None
        self.firmware_update = None
        self.firmware_update_fc0 = None
        self.serial_number = None
        self.file_list_parser = FileListing()
        # self.file_download_list = []
        self.last_file_request = datetime.datetime.utcnow()
        self.gprs_queue = []
        self.current_message = None

        if imei:
            self.on_login()

    def check_login(self):
        return True

    def send_command(self, command):
        pass

    def timeout_old(self):
        pass

    def send_gprs_from_queue(self):
        if self.current_message is None and self.firmware_update is None:
            if len(self.gprs_queue) >= 1:
                self.current_message = self.gprs_queue[0]
                self.current_message["sent"] = (datetime.datetime.utcnow()-EPOCH).total_seconds()
                self.send_data(self.current_message["request_bytes"])
                logger.info(self.current_message["request_bytes"])

    def match_response_to_message(self, gprs):
        if self.current_message is not None and len(self.gprs_queue) >= 1:
            if gprs.data_identifier == self.gprs_queue[0]["id"]:
                del self.gprs_queue[0]
                self.current_message = None
            else:
                logger.error(
                    "Identifier %s does not match item in queue: %s",
                    gprs.data_identifier,
                    self.gprs_queue[0]["id"]
                )
        self.send_gprs_from_queue()

    def queue_gprs(self, gprs, override_firmware=False):
        self.timeout_old()
        if self.firmware_update is not None and override_firmware is False:
            logger.info("Not sending message as in a firmware download sequence")
        elif gprs is None:
            logger.error("Trying to add null gprs item")
        else:
            message = gprs.as_bytes(self.message_counter)
            self.message_counter += 1

            if override_firmware:
                self.send_data(message)
            else:
                payload = {
                        "request_bytes": message,
                        "id": gprs.data_identifier,
                        "response_bytes": None,
                        "sent": 0,
                        "attempts": 0,
                    }
                self.gprs_queue.append(payload)
        self.send_gprs_from_queue()

    def get_client_details(self):
        start = super(MeitrackFirmwareClient, self).get_client_details()
        return (
                "meitrack, start: %s, ident: %s, remote: %s, age: %s\n%s\nBuffer: %s\nCurrent download: %s"
                "\nSDCard List: %s\nFirmware update: %s\nGPRS Queue Length: %s\n" % (
                    start, self.ident(), start, self.age(), self.get_download_details(), self.buffer,
                    self.current_download, self.file_list_parser, self.firmware_update,
                    len(self.gprs_queue)
                )
        )

    def get_download_details(self):
        return ""

    def ident(self):
        return "imei-%s" % (self.imei.decode())

    def on_login(self):
        super(MeitrackFirmwareClient, self).on_login()
        self.queue_event_report(self.imei, "Client firmware login")
        logger.log(13, "end of on firmware login")

    def on_client_close(self):
        self.queue_event_report(self.imei, "Client disconnected")

    def on_server_close(self):
        self.queue_event_report(self.imei, "Server disconnected")

    def reset_firmware_download_state(self):
        self.firmware_update = None
        self.firmware_update_fc0 = None

    def parse_firmware_binary(self, response):
        if response and response.get("version") and response.get("file_name"):
            self.firmware_update = FirmwareUpdate(
                self.imei,
                response.get("device_filter").encode(),
                MT_UPDATE_HOST.encode(),
                MT_UPDATE_PORT.encode(),
                response.get("file_name").encode(),
                base64.b64decode(response.get("firmware")),
                STAGE_SECOND
            )
            if self.firmware_update_fc0:
                self.firmware_update.parse_response(self.firmware_update_fc0)
            gprs = self.firmware_update.return_next_payload()
            self.queue_gprs(gprs, True)

    def parse_firmware_version(self, response):
        pass

    def parse_config(self, response):
        pass

    def process_connect_string(self, data):
        gprs_list = self.data_to_gprs_list(data)
        for gprs in gprs_list:
            if self.imei:
                if gprs.imei != self.imei:
                    logger.error("Received data packet for %s but client is %s", gprs.imei, self.imei)
            else:
                self.imei = gprs.imei
                self.on_login()
        self.process_gprs_list(gprs_list)

    def process_data(self, data):
        super().process_data(data)
        self.timeout_old()
        self.send_gprs_from_queue()
        gprs_list = self.data_to_gprs_list(data)
        return self.process_gprs_list(gprs_list)

    def data_to_gprs_list(self, data):
        if len(self.buffer) <= 65536:
            try:
                self.buffer = b"".join([self.buffer, data])
            except UnicodeDecodeError as err:
                logger.error("Unable to convert bytes to string %s with error: %s", data, err)
                raise ChatError("Unable to convert bytes to string")
        else:
            raise ChatError("Buffer too long")

        try:
            gprs_list, before, after = parse_data_payload(self.buffer, DIRECTION_CLIENT_TO_SERVER)
            if before != b'':
                logger.error("Got data before start of packet. Should not be possible.")
            logger.log(13, "Leftover bytes count %s, with data: %s", len(after), after)
            self.buffer = after
        except UnicodeDecodeError as err:
            logger.error("Unicode decode error on buffer %s, error: %s", self.buffer, err)
            logger.log(13, traceback.print_exc())
            raise ProtocolError("Problem parsing meitrack buffer, unable to decode buffer")
        except GPRSParseError as err:
            logger.error("Parsing error on buffer %s with error: %s", self.buffer, err)
            logger.log(13, traceback.print_exc())
            raise ProtocolError("Problem parsing meitrack buffer")

        return gprs_list

    def process_gprs_list(self, gprs_list):
        return_str = "%s " % self.ident()
        for gprs in gprs_list:
            if self.imei:
                if gprs.imei != self.imei:
                    logger.error("Received data packet for %s but client is %s", gprs.imei, self.imei)
            else:
                self.imei = gprs.imei
                self.on_login()

            self.match_response_to_message(gprs)

            if gprs.enclosed_data.command == b'FC7' and self.firmware_update is None:
                gprs = firmware_update.stc_cancel_ota_update(self.imei)
                self.queue_gprs(gprs)

            if gprs.enclosed_data.command in [b'FC0',] and self.firmware_update is None:
                if gprs.enclosed_data.command == b'FC0':
                    self.firmware_update_fc0 = gprs
                logger.info("Device %s is in firmware download mode", self.imei)
                get_firmware_event = get_firmware_binary_report(self.imei)
                self.queue_report(get_firmware_event)

            if self.firmware_update is not None:
                logger.log(15, "Firmware update in progress.")
                self.firmware_update.parse_response(gprs)
                next_message = self.firmware_update.return_next_payload()
                if next_message is not None:
                    self.queue_gprs(next_message, True)
                if self.firmware_update.is_finished:
                    self.reset_firmware_download_state()

        return return_str

    def check_for_timeout(self, date_dt):
        pass

    def request_client_location(self):
        pass

    def request_client_info(self):
        pass

    def request_client_photo_list(self, start=0):
        pass

    def request_client_take_photo(self, camera_number, file_name=None):
        pass

    def request_get_file(self, file_name, payload_start_index=0):
        pass

    def request_firmware_update(self):
        pass

    def request_cancel_firmware_update(self):
        if not self.imei:
            logger.error("Unable to request client to update firmware as client id not yet known")
        else:
            gprs = stc_cancel_ota_update(self.imei)
            self.queue_gprs(gprs, True)
            self.reset_firmware_download_state()
            self.queue_event_report(self.imei, "Request cancel firmware update")

    def restart_device(self):
        pass

    def restart_gps(self):
        pass

    def update_configuration(self):
        pass
