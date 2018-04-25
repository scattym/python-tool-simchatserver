import logging
from sim_chat_lib.meitrack.error import GPRSParseError
from sim_chat_lib.meitrack.command.common import Command, meitrack_date_to_datetime, datetime_to_meitrack_date
from sim_chat_lib.meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER
logger = logging.getLogger(__name__)


class SetCorneringCommand(Command):
    request_field_names = [
        "command", "angle"
    ]
    response_field_names = [
        "command", "response"
    ]

    def __init__(self, direction, payload=None):
        super(SetCorneringCommand, self).__init__(direction, payload=payload)
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

    test_command = SetCorneringCommand(0, b"A13,120")
    print(test_command.as_bytes())
    print(test_command)
    test_command = SetCorneringCommand(1, b"A13,OK")
    print(test_command.as_bytes())
    print(test_command)