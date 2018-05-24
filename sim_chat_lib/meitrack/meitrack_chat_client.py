import datetime
import logging
import os
import traceback

from meitrack.file_download import FileDownload
from meitrack.file_list import FileListing, FileListingError
from sim_chat_lib.chat import ChatClient as BaseChatClient
from sim_chat_lib.exception import Error as ChatError
from sim_chat_lib.exception import ProtocolError
from meitrack.error import GPRSParseError
from meitrack.error import GPRSError
from meitrack.gprs_protocol import parse_data_payload
from meitrack import build_message
from sim_chat_lib.meitrack.gprs_to_report import gprs_to_report, file_download_to_report, event_to_report
from sim_chat_lib.report import MeitrackConfigRequest


logger = logging.getLogger(__name__)

MT_PARTIAL_WAIT = int(os.environ.get("MT_PARTIAL_WAIT", "60"))
MT_NEW_FILE_WAIT = int(os.environ.get("MT_NEW_FILE_WAIT", "120"))
MT_FILE_LIST_WAIT = int(os.environ.get("MT_FILE_LIST_WAIT", "240"))


class MeitrackChatClient(BaseChatClient):
    def __init__(self, sock_fd, report_queue, imei):
        super(MeitrackChatClient, self).__init__(sock_fd, report_queue)
        self.imei = imei
        self.buffer = b''
        if imei:
            self.on_login()
        self.file_list_parser = FileListing()
        self.file_download_list = []
        self.last_file_request = datetime.datetime.now()

    def check_login(self):
        return True

    def send_command(self, command):
        pass

    def get_client_details(self):
        start = super(MeitrackChatClient, self).get_client_details()
        return "meitrack, ident: %s, remote: %s, age: %s\n%s\nBuffer: %s\nDownload list: %s\nSDCard List: %s\n" % (
            self.ident(), start, self.age(), self.get_download_details(), self.buffer,
            self.file_download_list, self.file_list_parser
        )

    def get_download_details(self):
        return_str = ""
        if self.file_download_list:
            return_str = "File Downloads\n"
            for file_download in self.file_download_list:
                return_str += "{}, {}, {}\n".format(
                    file_download.file_name,
                    file_download.expecting_packets,
                    file_download.fragment_list_as_string()
                )
        return return_str

    def ident(self):
        return "imei-%s" % (self.imei.decode())

    def on_login(self):
        super(MeitrackChatClient, self).on_login()
        config_request = MeitrackConfigRequest()
        config_request.imei = self.imei
        logger.log(13, "Add config request to queue %s", config_request)
        self.queue_config_request(config_request)
        logger.log(13, "end of on login")
        report = event_to_report(self.imei, "Client login")
        queue_result = self.queue_report(report)
        logger.log(13, "Queue add result was %s", queue_result)

    def on_client_close(self):
        report = event_to_report(self.imei, "Client disconnected")
        queue_result = self.queue_report(report)
        logger.log(13, "Queue add result was %s", queue_result)

    def on_server_close(self):
        report = event_to_report(self.imei, "Server disconnected")
        queue_result = self.queue_report(report)
        logger.log(13, "Queue add result was %s", queue_result)

    def parse_config(self, response):
        logger.info("Parsing config response %s", response)
        if not response:
            logger.error("No response to parse.")
            return
        if response.get("heartbeat_interval") is not None:
            gprs = build_message.stc_set_heartbeat_interval(self.imei, response.get("heartbeat_interval"))
            self.send_data(gprs.as_bytes())
        if response.get("time_interval") is not None:
            gprs = build_message.stc_set_tracking_by_time_interval(self.imei, response.get("time_interval"))
            self.send_data(gprs.as_bytes())
        if response.get("cornering_angle") is not None:
            gprs = build_message.stc_set_cornering_angle(self.imei, response.get("cornering_angle"))
            self.send_data(gprs.as_bytes())
        if response.get("tracking_by_distance") is not None:
            gprs = build_message.stc_set_tracking_by_distance(self.imei, response.get("tracking_by_distance"))
            self.send_data(gprs.as_bytes())
        if response.get("time_zone_offset_minutes") is not None:
            gprs = build_message.stc_set_time_zone(self.imei, response.get("time_zone_offset_minutes"))
            self.send_data(gprs.as_bytes())
        if response.get("driving_license_type") is not None:
            gprs = build_message.stc_set_driver_license_type(self.imei, response.get("driving_license_type"))
            self.send_data(gprs.as_bytes())
        if response.get("fatigue_driving_consecutive_driving_time") is not None or \
                response.get("fatigue_driving_alert_time") is not None or \
                response.get("fatigue_driving_acc_off_time_mins") is not None:
            consec = response.get("fatigue_driving_consecutive_driving_time") or 480
            alert = response.get("fatigue_driving_alert_time") or 300
            acc_off = response.get("fatigue_driving_acc_off_time_mins") or 0
            gprs = build_message.stc_set_fatigue_driving_alert_time(
                self.imei,
                consec,
                alert,
                acc_off
            )
            self.send_data(gprs.as_bytes())
        if response.get("idle_alert_consecutive_speed_time") is not None or \
                response.get("idle_alert_speed_kmh") is not None or \
                response.get("idle_alert_alert_time") is not None:
            consec = response.get("idle_alert_consecutive_speed_time") or 480
            speed = response.get("fatigue_driving_acc_off_time_mins") or 0
            alert_time = response.get("idle_alert_alert_time") or 300

            gprs = build_message.stc_set_idle_alert_time(
                self.imei,
                consec,
                speed,
                alert_time,
            )
            self.send_data(gprs.as_bytes())
        if response.get("speeding_alert_speed") is not None or \
                response.get("speeding_alert_disabled") is not None:
            speed = response.get("speeding_alert_speed") or 480
            disabled = response.get("speeding_alert_disabled") or True
            gprs = build_message.stc_set_speeding_alert(
                self.imei,
                speed,
                disabled,
            )
            self.send_data(gprs.as_bytes())
        if response.get("driving_license_validity_time") is not None:
            gprs = build_message.stc_set_driver_license_validity_time(
                self.imei,
                response.get("driving_license_validity_time")
            )
            self.send_data(gprs.as_bytes())

    def process_data(self, data):
        if len(self.buffer) <= 65536:
            try:
                self.buffer = b"".join([self.buffer, data])
            except UnicodeDecodeError as err:
                logger.error("Unable to convert bytes to string %s", data)
                raise ChatError("Unable to convert bytes to string")
        else:
            raise ChatError("Buffer too long")

        try:
            gprs_list, before, after = parse_data_payload(self.buffer)
        except UnicodeDecodeError as err:
            logger.error("Unicode decode error on buffer %s", self.buffer)
            logger.log(13, traceback.print_exc())
            raise ProtocolError("Problem parsing meitrack buffer, unable to decode buffer")
        except GPRSParseError as err:
            logger.error("Parsing error on buffer %s", self.buffer)
            logger.log(13, traceback.print_exc())
            raise ProtocolError("Problem parsing meitrack buffer")

        return_str = "%s " % self.ident()
        for gprs in gprs_list:
            if not self.imei:
                self.imei = gprs.imei
            # print(gprs)
            report = gprs_to_report(gprs)
            queue_result = self.queue_report(report)
            if not queue_result:
                logger.error("Unable to add record to queue: %s", (gprs.as_bytes()))
            try:
                return_str += (gprs.as_bytes()).decode()
            except UnicodeDecodeError as err:
                logger.error("Unable to decode response to send to masters")
                return_str += "Binary data"

            try:
                packet_count, packet_number = self.file_list_parser.add_packet(gprs)
                if packet_count and packet_number:
                    if packet_number % 8 == 7 and packet_count > packet_number+1:
                        self.request_client_photo_list(packet_number+1)
                    report = event_to_report(
                        self.imei, "Photo list fragment {} of {}".format(packet_number+1, packet_count)
                    )
                    queue_result = self.queue_report(report)
                logger.log(13, "Queue add result was %s", queue_result)

            except FileListingError as err:
                logger.error("Error adding packet to file list %s. Clearing list.", err)
                self.file_list_parser.clear_list()

            if gprs and gprs.enclosed_data and gprs.enclosed_data["event_code"] == b'39':
                if len(self.file_download_list) == 0:
                    logger.log(13, "No current downloads. Asking for file.")

                    ask_for_file = build_message.stc_request_get_file(
                        self.imei,
                        gprs.enclosed_data["file_name"]
                    )
                    self.send_data(ask_for_file.as_bytes())

                else:
                    logger.log(13,
                        "Download already in progress, queue file for download later %s",
                        gprs.enclosed_data["file_name"]
                    )
                    # self.download_list.append(gprs.enclosed_data["file_name"])

            if gprs and gprs.enclosed_data:
                file_name, num_packets, packet_number, file_bytes = gprs.enclosed_data.get_file_data()
                if file_name and file_bytes:
                    # Reset last file request so that we don't overload the client with requsts
                    # while it is already sending a file.
                    self.last_file_request = datetime.datetime.now()
                    return_str += "File: %s, packet: %s, of: %s\n" % (
                        file_name.decode(),
                        packet_number.decode(),
                        num_packets.decode()
                    )
                    packet_number_int = int(packet_number.decode())
                    num_packets_int = int(num_packets.decode())
                    report = event_to_report(
                        self.imei, "Photo fragment {} of {}".format(packet_number_int+1, num_packets_int)
                    )
                    queue_result = self.queue_report(report)
                    logger.log(13, "Queue add result was %s", queue_result)

                    found = False
                    for file_download in self.file_download_list:
                        if file_download.file_name == file_name:
                            found = True
                            file_download.add_packet(gprs)
                    if not found:
                        file_download = FileDownload(file_name)
                        file_download.add_packet(gprs)
                        self.file_download_list.append(file_download)

                    if packet_number_int % 8 == 7 and num_packets_int > packet_number_int+1:
                        self.request_get_file(file_name, packet_number_int+1)

                for running_download in self.file_download_list:
                    if running_download.is_complete():
                        logger.log(13, "File is complete. Sending to geotool. ")
                        report = file_download_to_report(self.imei, running_download)
                        self.queue_report(report)
                        self.file_download_list.remove(running_download)
                        self.file_list_parser.remove_item(running_download.file_name)

                else:
                    # If we haven't received any file data for a while
                    if datetime.datetime.now() - self.last_file_request > datetime.timedelta(seconds=MT_PARTIAL_WAIT):
                        # If we have partial downloads stored in memory then try to download more of that file
                        if len(self.file_download_list) > 0:
                            logger.log(13, "We have files in the file download list %s", self.file_download_list)
                            file_name = self.file_download_list[-1].file_name
                            next_packet = self.file_download_list[-1].next_packet()
                            self.request_get_file(file_name, next_packet)
                        # else ask for data from the sdcard
                        elif len(self.file_list_parser.file_arr) > 0 and datetime.datetime.now() - self.last_file_request > datetime.timedelta(seconds=MT_NEW_FILE_WAIT):
                            file_name = self.file_list_parser.file_arr[-1]
                            next_packet = 0
                            self.request_get_file(file_name, 0)
                        # else if we don't have either of those and it's been long enough then
                        # ask for a full file listing from the device.
                        elif datetime.datetime.now() - self.last_file_request > datetime.timedelta(seconds=MT_FILE_LIST_WAIT):
                            self.request_client_photo_list()

        if before != b'':
            logger.error("Got data before start of packet. Should not be possible.")
        logger.log(13, "Leftover bytes count %s, with data: %s", len(after), after)
        self.buffer = after
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
                logger.log(13, gprs)
                logger.log(13, gprs.as_bytes())
                self.send_data((gprs.as_bytes()))
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")

    def request_client_photo_list(self, start=0):
        if not self.imei:
            logger.error("Unable to request photo list as client id not yet known")
        else:
            try:
                gprs = build_message.stc_request_photo_list(self.imei, start)
                self.send_data((gprs.as_bytes()))
                self.last_file_request = datetime.datetime.now()
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
            logger.error("Unable to request client to retrieve photo as client id not yet known")
        elif file_name is None:
            logger.error("File name is not known. %s", file_name)
            traceback.print_exc()
            raise ProtocolError("Filename not calculated.")
        else:
            try:
                gprs = build_message.stc_request_get_file(self.imei, file_name, payload_start_index)
                self.send_data((gprs.as_bytes()))
                self.last_file_request = datetime.datetime.now()
            except GPRSError as err:
                logger.error("Failed to create gprs payload to send.")
