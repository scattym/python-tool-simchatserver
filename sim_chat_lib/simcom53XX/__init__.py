
import datetime
import logging
from . import simcom53XX_chat_client_v1
from . import simcom53XX_chat_client_v2

logger = logging.getLogger(__name__)
DEVICE_NAME_LIST = ["5320", "5360"]


def parse_client_connect(socket, report_queue, connect_line):
    client_details = {}
    logger.log(13, connect_line)
    byte_converter = lambda x: x.encode()
    if isinstance(connect_line, str):
        byte_converter = lambda x: x

    if connect_line[0:6] != byte_converter('C0NXN:'):
        logger.error("No start string: %s, %s", connect_line, connect_line[0:6])
        return None

    connect_string_list = connect_line.rstrip().split(byte_converter(':'))
    if len(connect_string_list) >= 2:
        client_details = {
            "version": None,
            "last_tick": datetime.datetime.now(),
            "imei": connect_string_list[1],
            "proto_version": 1,
        }

    if len(connect_string_list) >= 3:
        client_details["version"] = connect_string_list[2]
    if len(connect_string_list) >= 4:
        try:
            client_details["proto_version"] = int(connect_string_list[3])
        except ValueError as err:
            client_details["proto_version"] = 1

    if len(connect_string_list) >= 5:
        client_details["device_name"] = connect_string_list[4]
    if len(connect_string_list) >= 6:
        client_details["seed"] = connect_string_list[5]
    if len(connect_string_list) >= 7:
        client_details["login_hash"] = connect_string_list[6]

    if client_details["proto_version"] == 1 or (client_details.get("device_name") in DEVICE_NAME_LIST):
        logger.log(13, "%s is a version 1 client", client_details["imei"])
        return create_chat_client(socket, report_queue, client_details)
    logger.error("Failed to create an instance: %s", client_details)
    return None


def create_chat_client(socket, report_queue, client_details):
    if client_details.get("proto_version") == 1:
        logger.log(13, "Creating simcom v1 client")
        return simcom53XX_chat_client_v1.ChatClient(
            socket,
            report_queue,
            client_details.get("imei"),
            client_details.get("version")
        )
    if client_details.get("proto_version") == 2:
        logger.log(13, "Creating simcom v2 client")
        return simcom53XX_chat_client_v2.ChatClient(
            socket,
            report_queue,
            client_details.get("imei"),
            client_details.get("version"),
            client_details.get("proto_version"),
            client_details.get("device_name"),
            client_details.get("seed"),
            client_details.get("login_hash"),
        )
