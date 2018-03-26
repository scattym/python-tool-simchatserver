import logging
import datetime
from sim_chat_lib.meitrack.gprs_protocol import GPRS, parse_data_payload
from sim_chat_lib.meitrack.error import GPRSParseError
from sim_chat_lib.meitrack.meitrack_chat_client import MeitrackChatClient

logger = logging.getLogger(__name__)


def parse_client_connect(sock_fd, connect_line):
    client_details = {}
    logger.debug(connect_line)
    if connect_line[0:2] != '$$':
        logger.error("No start string: %s, %s", connect_line, connect_line[0:6])
        return None

    client_details = {}
    try:
        gprs_list, before, after = parse_data_payload(connect_line)
        for gprs in gprs_list:
            if gprs.imei:
                client_details["imei"] = gprs.imei
                client_details["last_tick"] = datetime.datetime.now()
                return create_chat_client(sock_fd, client_details)
    except GPRSParseError:
        logger.error("Unable to parse connect string for meitrack device.")
    return None


def create_chat_client(socket, client_details):
    logger.debug("Creating meitrack gprs client")
    return meitrack_chat_client.MeitrackChatClient(
        socket,
        client_details.get("imei"),
    )
