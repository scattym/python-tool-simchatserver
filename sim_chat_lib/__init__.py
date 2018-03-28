from sim_chat_lib import simcom53XX
from sim_chat_lib import meitrack
import logging

from sim_chat_lib.exception import ProtocolError

logger = logging.getLogger(__name__)


def check_login(imei_line):
    pass
    # if len(imei_line) == 0:
    #     raise LoginError("No login information")


def parse_client_connect(sock_fd, task_queue, connect_line):
    # if len(connect_line) == 0:
    #     raise ProtocolError("No connect information")
    # imei = None

    try:
        client = simcom53XX.parse_client_connect(sock_fd, task_queue, connect_line)
        if client is None:
            client = meitrack.parse_client_connect(sock_fd, task_queue, connect_line)
    except UnicodeDecodeError as err:
        logger.error("Unable to decode data: %s", connect_line)
        raise ProtocolError("Unable to decode data: %s" % (connect_line,))

    return client
