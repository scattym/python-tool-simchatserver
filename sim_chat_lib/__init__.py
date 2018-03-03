import simcom53XX


def check_login(imei_line):
    pass
    # if len(imei_line) == 0:
    #     raise LoginError("No login information")


def parse_client_connect(sock_fd, connect_line):
    # if len(connect_line) == 0:
    #     raise ProtocolError("No connect information")
    # imei = None

    client = simcom53XX.parse_client_connect(sock_fd, connect_line)

    return client