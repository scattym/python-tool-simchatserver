import logging
import datetime
from sim_chat_lib.meitrack.gprs_protocol import GPRS, parse_data_payload
from sim_chat_lib.meitrack.error import GPRSParseError
from sim_chat_lib.meitrack.meitrack_chat_client import MeitrackChatClient

logger = logging.getLogger(__name__)


def parse_client_connect(sock_fd, report_queue, connect_line):
    client_details = {}
    logger.debug(connect_line)
    if connect_line[0:2] != b'$$' and connect_line[0:2] != '$$':
        logger.error("No start string: %s, %s", connect_line, connect_line[0:6])
        return None

    client_details = {}
    try:
        gprs_list, before, after = parse_data_payload(connect_line)
        for gprs in gprs_list:
            if gprs.imei:
                client_details["imei"] = gprs.imei
                client_details["last_tick"] = datetime.datetime.now()
                chat_client = create_chat_client(sock_fd, report_queue, client_details)
                if chat_client:
                    # Re-encode connect line as we decoded it on the
                    # way into this function
                    chat_client.process_data(connect_line)
                return chat_client
    except GPRSParseError:
        logger.error("Unable to parse connect string for meitrack device.")
    return None


def create_chat_client(socket, report_queue, client_details):
    logger.debug("Creating meitrack gprs client")
    return meitrack_chat_client.MeitrackChatClient(
        socket,
        report_queue,
        client_details.get("imei"),
    )
