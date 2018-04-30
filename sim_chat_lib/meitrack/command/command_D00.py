import datetime
import logging

from sim_chat_lib.meitrack.command import common
from sim_chat_lib.meitrack.error import GPRSParseError
from sim_chat_lib.meitrack.command.common import Command, meitrack_date_to_datetime, datetime_to_meitrack_date
from sim_chat_lib.meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER
logger = logging.getLogger(__name__)


class FileDownloadCommand(Command):
    request_field_names = [
        "command", "file_name", "data_packet_start_number"
    ]
    response_field_names = [
        "command", "file_name", "number_of_data_packets", "data_packet_number", "file_bytes"
    ]

    def __init__(self, direction, payload=None):
        super(FileDownloadCommand, self).__init__(direction, payload=payload)
        logger.debug(payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload, 4)

        self.field_dict['date_time'] = datetime.datetime.now()
        file_name = self.field_dict.get("file_name")
        if file_name:
            # 180428115949_C1E11_N1U1D1.jpg
            file_name_arr = file_name.split(b"_")
            if len(file_name_arr) == 3:
                date = common.meitrack_date_to_datetime(file_name_arr[0])
                if date:
                    self.field_dict["date_time"] = date

        logger.debug(self.field_dict)
