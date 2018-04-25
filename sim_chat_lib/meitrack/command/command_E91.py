import logging
from sim_chat_lib.meitrack.error import GPRSParseError
from sim_chat_lib.meitrack.command.common import Command, meitrack_date_to_datetime, datetime_to_meitrack_date
from sim_chat_lib.meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER
logger = logging.getLogger(__name__)


class RequestDeviceInfoCommand(Command):
    request_field_names = [
        "command"
    ]
    response_field_names = [
        "command", "firmware_version", "serial_number"
    ]

    def __init__(self, direction, payload=None):
        super(RequestDeviceInfoCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)


if __name__ == '__main__':
    log_level = 11 - 11

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    tests = [
        b"""E91""",
        b"""E91,FWV1.00,12345678""",
    ]

    test_command = RequestDeviceInfoCommand(0, b"E91")
    print(test_command.as_bytes())
    print(test_command)
    test_command = RequestDeviceInfoCommand(1, b"E91,FWV1.00,12345678")
    print(test_command.as_bytes())
    print(test_command)