import base64

import datetime
import logging
import os
import traceback

from meitrack.build_message import stc_restart_gps, stc_restart_gsm, stc_set_output_pin, stc_set_snapshot_parameters
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
from sim_chat_lib.meitrack.geotool_config_to_gprs_list import config_to_gprs
from sim_chat_lib.meitrack.gprs_to_report import gprs_to_report, get_firmware_binary_report, get_firmware_version_report
from sim_chat_lib.report import MeitrackConfigRequest


logger = logging.getLogger(__name__)

MT_PARTIAL_WAIT = int(os.environ.get("MT_PARTIAL_WAIT", "120"))
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


class MeitrackChatClient(BaseChatClient):
    def __init__(self, sock_fd, report_queue, imei):
        super(MeitrackChatClient, self).__init__(sock_fd, report_queue)
        self.message_counter = 0
        self.imei = imei
        self.buffer = b''
        self.current_download = None
        self.current_packet = None
        self.firmware_update = None
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
        if self.current_message is not None and len(self.gprs_queue) >= 1:
            now = (datetime.datetime.utcnow()-EPOCH).total_seconds()
            if self.gprs_queue[0]["sent"] != 0 and (now - self.gprs_queue[0]["sent"]) >= 60:
                logger.error("Timing out %s", self.current_message)
                self.current_message = None
                del self.gprs_queue[0]
        self.send_gprs_from_queue()

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
        start = super(MeitrackChatClient, self).get_client_details()
        return (
                "meitrack, start: %s, ident: %s, remote: %s, age: %s\n%s\nBuffer: %s\nCurrent download: %s"
                "\nSDCard List: %s\nFirmware update: %s\nGPRS Queue Length: %s\n" % (
                    start, self.ident(), start, self.age(), self.get_download_details(), self.buffer,
                    self.current_download, self.file_list_parser, self.firmware_update,
                    len(self.gprs_queue)
                )
        )

    def get_download_details(self):
        return_str = ""
        if self.current_download:
            return_str = "File Download: "
            return_str += "{}, {}\n".format(
                self.current_download,
                self.current_packet
            )
        return return_str

    def ident(self):
        return "imei-%s" % (self.imei.decode())

    def on_login(self):
        super(MeitrackChatClient, self).on_login()
        self.queue_event_report(self.imei, "Client login")
        logger.log(13, "end of on login")

    def on_client_close(self):
        self.queue_event_report(self.imei, "Client disconnected")

    def on_server_close(self):
        self.queue_event_report(self.imei, "Server disconnected")

    def reset_firmware_download_state(self):
        self.firmware_update = None

    def parse_firmware_binary(self, response):
        pass

    def parse_firmware_version(self, response):
        if response and response.get("version") and response.get("file_name"):
            self.firmware_update = FirmwareUpdate(
                self.imei,
                response.get("device_filter").encode(),
                MT_UPDATE_HOST.encode(),
                MT_UPDATE_PORT.encode(),
                response.get("file_name").encode(),
                b"",
                STAGE_FIRST
            )
            gprs = self.firmware_update.return_next_payload()
            self.queue_gprs(gprs, True)

    def parse_config(self, response):
        logger.info("Parsing config response %s", response)
        if not response:
            logger.error("No response to parse.")
            return
        if self.firmware_update is None:
            gprs_list, event_report_list = config_to_gprs(response, self.imei)
            for gprs in gprs_list:
                self.queue_gprs(gprs)
            for event_report in event_report_list:
                self.queue_report(event_report)

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

            if self.firmware_update is not None:
                logger.log(15, "Firmware update in progress.")
                self.firmware_update.parse_response(gprs)
                next_message = self.firmware_update.return_next_payload()
                if next_message is not None:
                    self.queue_gprs(next_message, True)
                if self.firmware_update.is_finished:
                    self.reset_firmware_download_state()
            else:
                # print(gprs)
                report_list = gprs_to_report(gprs)
                for report in report_list:
                    queue_result = self.queue_report(report)
                    if not queue_result:
                        logger.error("Unable to add record to queue: %s", (gprs.as_bytes()))
                try:
                    return_str += (gprs.as_bytes()).decode()
                except UnicodeDecodeError as err:
                    logger.error("Unable to decode response to send to masters with error: %s", err)
                    return_str += "Binary data"

                try:
                    packet_count, packet_number = self.file_list_parser.add_packet(gprs)
                    if packet_count is not None and packet_number is not None:
                        # if packet_number % 8 == 7 and packet_count > packet_number+1:
                        #     self.request_client_photo_list(packet_number+1)
                        self.queue_event_report(
                            self.imei, "Photo list fragment {} of {}".format(packet_number+1, packet_count)
                        )
                except FileListingError as err:
                    logger.error("Error adding packet to file list %s. Clearing list.", err)
                    self.file_list_parser.clear_list()

                # logic no longer required as the images are automatically sent to the headend.
                # We are still issuing a file list after 480s so any orphans should get cleaned
                # up by that logic instead.
                # if gprs and gprs.enclosed_data and gprs.enclosed_data["event_code"] == b'39':
                #     self.file_list_parser.add_item(gprs.enclosed_data["file_name"])
                #     self.queue_event_report(
                #         self.imei, "New photo on device {}".format(gprs.enclosed_data["file_name"])
                #     )

                if gprs and gprs.enclosed_data:
                    file_name, num_packets, packet_number, file_bytes = gprs.enclosed_data.get_file_data()
                    if file_name and file_bytes:
                        # Reset last file request so that we don't overload the client with requests
                        # while it is already sending a file.
                        self.last_file_request = datetime.datetime.utcnow()
                        packet_number_int = int(packet_number.decode())
                        num_packets_int = int(num_packets.decode())
                        self.current_download = file_name
                        self.current_packet = packet_number_int

                        # if packet_number_int % 8 == 7 and num_packets_int > packet_number_int+1:
                        #     self.request_get_file(file_name, packet_number_int+1)
                        return_str += "File: %s, packet: %s, of: %s\n" % (
                            file_name.decode(),
                            packet_number_int+1,
                            num_packets_int
                        )
                        if num_packets_int == packet_number_int+1:
                            self.current_download = None
                            self.current_packet = None
                            self.file_list_parser.remove_item(file_name)

        return return_str

    def check_for_timeout(self, date_dt):
        self.timeout_old()
        self.send_gprs_from_queue()

        logger.debug("Checking for timeout for client %s", self.imei)
        if self.firmware_update is not None:
            logger.log(13, "Firmware update in progress. Don't send timed commands.")
            if self.firmware_update.is_finished:
                self.reset_firmware_download_state()
            else:
                next_message = self.firmware_update.return_next_payload()
                if next_message is not None:
                    self.queue_gprs(next_message, True)
            return None

        # Early check to keep this function running as quickly as possible as it is
        # called in every outer loop
        if self.current_download is not None or self.file_list_parser.num_files > 0:
            # If we haven't received any file data for a while
            if date_dt - self.last_file_request > MT_PARTIAL_WAIT_DELTA:

                # If we have partial downloads stored in memory then try to download more of that file
                if self.current_download is not None:
                    logger.log(
                        13,
                        "We have a stuck download. Resuming %s at fragment %s",
                        self.current_download,
                        self.current_packet
                    )
                    self.request_get_file(self.current_download, self.current_packet+1)

                # else ask for data from the sdcard
                elif self.file_list_parser.num_files > 0 and date_dt - self.last_file_request > MT_NEW_FILE_WAIT_DELTA:

                    file_name = self.file_list_parser.file_arr[-1]
                    self.request_get_file(file_name, 0)

        # else if we don't have either of those and it's been long enough then
        # ask for a full file listing from the device.
        elif date_dt - self.last_file_request > MT_FILE_LIST_WAIT_DELTA:
            self.request_client_photo_list()

    def request_client_location(self):
        if not self.imei:
            logger.error("Unable to request location as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_location_message(self.imei)
                self.queue_gprs(gprs)
                self.queue_event_report(self.imei, "Request client location")
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send. Error: %s", err)

    def request_client_info(self):
        if not self.imei:
            logger.error("Unable to request client info as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_device_info(self.imei)
                self.queue_gprs(gprs)
                self.queue_event_report(self.imei, "Request device information")
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send. Error %s", err)

    def request_client_photo_list(self, start=0):
        if not self.imei:
            logger.error("Unable to request photo list as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_photo_list(self.imei, start)
                self.queue_gprs(gprs)
                self.last_file_request = datetime.datetime.utcnow()
                self.queue_event_report(self.imei, "Request photo list")
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send. Error: %s", err)

    def request_client_take_photo(self, camera_number, file_name=None):
        if not self.imei:
            logger.error("Unable to request client to take a photo as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_take_photo(self.imei, camera_number, file_name)
                self.queue_gprs(gprs)
                self.queue_event_report(self.imei, "Request take photo camera {}".format(camera_number))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send. Error: %s", err)

    def request_get_file(self, file_name, payload_start_index=0):
        if not self.imei:
            logger.error("Unable to request client to retrieve photo as client id not yet known")
        elif file_name is None:
            logger.error("File name is not known. %s", file_name)
            traceback.print_exc()
            raise ProtocolError("Filename not calculated.")
        else:
            try:
                gprs = build_message.stc_request_get_file(self.imei, file_name, payload_start_index)
                self.queue_gprs(gprs)
                self.last_file_request = datetime.datetime.utcnow()
                self.queue_event_report(
                    self.imei,
                    "Request file {} from fragment {}".format(file_name, payload_start_index+1)
                )
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send. Error: %s", err)

    def request_firmware_update(self):
        if not self.imei:
            logger.error("Unable to request client to update firmware as client id not yet known")
        else:
            get_firmware_event = get_firmware_version_report(self.imei)
            self.queue_report(get_firmware_event)
            self.queue_event_report(self.imei, "Request get firmware version")

    def request_cancel_firmware_update(self):
        if not self.imei:
            logger.error("Unable to request client to update firmware as client id not yet known")
        else:
            gprs = stc_cancel_ota_update(self.imei)
            self.queue_gprs(gprs, True)
            self.reset_firmware_download_state()
            self.queue_event_report(self.imei, "Request cancel firmware update")

    def restart_device(self):
        if not self.imei:
            logger.error("Unable to request client to update firmware as client id not yet known")
        else:
            gprs = stc_restart_gsm(self.imei)
            self.queue_gprs(gprs, True)
            self.queue_event_report(self.imei, "Request device gsm restart")

    def restart_gps(self):
        if not self.imei:
            logger.error("Unable to request client to update firmware as client id not yet known")
        else:
            gprs = stc_restart_gps(self.imei)
            self.queue_gprs(gprs, True)
            self.queue_event_report(self.imei, "Request gps restart")

    def set_output(self, pin, state):
        if not self.imei:
            logger.error("Unable to request client to update firmware as client id not yet known")
        else:
            gprs = stc_set_output_pin(self.imei, 1, pin, state)
            self.queue_gprs(gprs, True)
            self.queue_event_report(self.imei, "Request set pin %s to state %s" % (pin, state))

    def set_snapshot_parameters(self, event_code=1, interval=20, count=1, upload=1, delete=1):
        if not self.imei:
            logger.error("Unable to request client to update firmware as client id not yet known")
        else:
            gprs = stc_set_snapshot_parameters(self.imei, event_code, interval, count, upload, delete)
            self.queue_gprs(gprs, True)
            self.queue_event_report(
                self.imei,
                "Snapshot parameters sent to device. Event: %s, Interval: %s, Count: %s, Upload: %s, Delete: %s" % (
                    event_code,
                    interval,
                    count,
                    upload,
                    delete,
                )
            )

    def update_configuration(self):
        if not self.imei:
            logger.error("Unable to request client to update configuration as client id not yet known")
        else:
            config_request = MeitrackConfigRequest()
            config_request.imei = self.imei
            logger.log(13, "Add config request to queue %s", config_request)
            self.queue_config_request(config_request)
            self.queue_event_report(self.imei, "Request client config")
