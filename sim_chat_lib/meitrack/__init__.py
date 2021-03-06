import logging
import datetime

from meitrack.common import DIRECTION_CLIENT_TO_SERVER
from meitrack.gprs_protocol import GPRS, parse_data_payload
from meitrack.error import GPRSParseError
from sim_chat_lib.meitrack import meitrack_firmware_client
from sim_chat_lib.meitrack.meitrack_chat_client import MeitrackChatClient

logger = logging.getLogger(__name__)


def parse_client_connect(sock_fd, report_queue, connect_line):
    client_details = {}
    logger.log(13, connect_line)
    if connect_line[0:2] != b'$$' and connect_line[0:2] != '$$':
        logger.error("No start string: %s, %s", connect_line, connect_line[0:6])
        return None

    client_details = {}
    try:
        gprs_list, before, after = parse_data_payload(connect_line, DIRECTION_CLIENT_TO_SERVER)
        for gprs in gprs_list:
            if gprs.imei:
                client_details["imei"] = gprs.imei
                client_details["last_tick"] = datetime.datetime.utcnow()
                if b'FC0' in gprs.enclosed_data.payload:
                    chat_client = create_firmware_client(sock_fd, report_queue, client_details)

                else:
                    chat_client = create_chat_client(sock_fd, report_queue, client_details)

                if chat_client:
                    # Re-encode connect line as we decoded it on the
                    # way into this function
                    chat_client.process_connect_string(connect_line)
                return chat_client
    except GPRSParseError:
        logger.error("Unable to parse connect string for meitrack device.")
    return None


def create_chat_client(socket, report_queue, client_details):
    logger.log(13, "Creating meitrack gprs client")
    return meitrack_chat_client.MeitrackChatClient(
        socket,
        report_queue,
        client_details.get("imei"),
    )


def create_firmware_client(socket, report_queue, client_details):
    logger.log(13, "Creating meitrack firmware gprs client")
    return meitrack_firmware_client.MeitrackFirmwareClient(
        socket,
        report_queue,
        client_details.get("imei"),
    )