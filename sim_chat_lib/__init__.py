from sim_chat_lib import simcom53XX
from sim_chat_lib import meitrack


def check_login(imei_line):
    pass
    # if len(imei_line) == 0:
    #     raise LoginError("No login information")


def parse_client_connect(sock_fd, task_queue, connect_line):
    # if len(connect_line) == 0:
    #     raise ProtocolError("No connect information")
    # imei = None

    client = simcom53XX.parse_client_connect(sock_fd, task_queue, connect_line)
    if client is None:
        client = meitrack.parse_client_connect(sock_fd, task_queue, connect_line)

    return client
