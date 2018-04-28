import datetime
import logging

from sim_chat_lib.meitrack.command.event import event_to_name
from sim_chat_lib.meitrack.error import GPRSParseError

logger = logging.getLogger(__name__)


class Command(object):
    def __init__(self, direction, payload=None):
        self.payload = payload
        self.direction = direction
        self.field_name_selector = []
        self.field_dict = {}

    def __str__(self):
        result_str = ""
        result_str = "%s\n" % (self.payload,)
        for field in self.field_name_selector:
            result_str += "\tField %s has value %s\n" % (field, self.field_dict[field])
        return result_str

    def as_bytes(self):
        fields = []
        if self.field_name_selector:
            for field in self.field_name_selector:
                if self.field_dict.get(field):
                    if field == "date_time":
                        logger.debug("Date field is %s", self.field_dict.get(field))
                        fields.append(datetime_to_meitrack_date(self.field_dict.get(field)))
                    else:
                        fields.append(self.field_dict.get(field))
        if fields:
            return b','.join(fields)
        else:
            return self.payload

    def __getitem__(self, item):
        if item in self.field_dict:
            return self.field_dict[item]
        return None
        # raise AttributeError("Field %s not set" % (item,))

    def __getattr__(self, item):
        if item in self.field_dict:
            return self.field_dict[item]
        return None
        # raise AttributeError("Field %s not set" % (item,))

    def parse_payload(self, payload, max_split=None):
        if max_split:
            fields = payload.split(b',', max_split)
        else:
            fields = payload.split(b',')
        if len(fields) < 1:
            raise GPRSParseError("Field length does not include event code", self.payload)
        if self.field_name_selector is None:
            logger.debug("No field names set")
            return

        if len(self.field_name_selector) < len(fields):
            print("%s %s" % (len(fields), len(self.field_name_selector)))
            print(payload)
            raise GPRSParseError(
                "Incorrect number of fields for data. Data field length is ", len(fields),
                " but should be ", len(self.field_name_selector), ". Fields should be ",
                str(self.field_name_selector)
            )
        for i in range(0, len(fields)):
            field_name = self.field_name_selector[i]
            if field_name == "date_time":
                self.field_dict[field_name] = meitrack_date_to_datetime(fields[i])
            else:
                self.field_dict[field_name] = fields[i]

    def get_analog_input_value(self, input_number):
        if self.field_dict.get("analog_input_value"):
            analog_list = self.field_dict.get("analog_input_value").split(b"|")
            if input_number <= len(analog_list):
                print(analog_list[input_number-1])
                print(int(analog_list[input_number-1], 16))
                return int(analog_list[input_number-1], 16) / 100

    def get_battery_voltage(self):
        return self.get_analog_input_value(4)

    def get_battery_level(self):
        battery_voltage = self.get_battery_voltage()
        if battery_voltage:
            return int(self.get_battery_voltage() / 4.2 * 100)

    def get_base_station_info(self):
        if self.field_dict.get("base_station_info"):
            fields = self.field_dict.get("base_station_info").split(b"|")
            if len(fields) == 4:
                return_dict = {
                    "mcc": fields[0],
                    "mnc": fields[1],
                    "lac": str(int(fields[2], 16)).encode(),
                    "ci": str(int(fields[3], 16)).encode(),
                    "gsm_signal_strength": self.get_gsm_signal_strength()
                }
                return return_dict

    def get_gsm_signal_strength(self):
        if self.field_dict.get("gsm_signal_strength"):
            return self.field_dict.get("gsm_signal_strength")

    def get_file_data(self):
        if self.field_dict.get("file_bytes"):
            return (
                self.field_dict.get("file_name"),
                self.field_dict.get("number_of_data_packets"),
                self.field_dict.get("data_packet_number"),
                self.field_dict.get("file_bytes")
            )
        else:
            return None, None, None, None

    def get_event_name(self):
        if self.field_dict.get("event_code"):
            return event_to_name(self.field_dict.get("event_code"))


def meitrack_date_to_datetime(date_time):
    # yymmddHHMMSS
    date_time = "%s%s" % (date_time.decode(), "Z")
    d = datetime.datetime.strptime(date_time, "%y%m%d%H%M%SZ")
    return d


def datetime_to_meitrack_date(date_time):
    return date_time.strftime("%y%m%d%H%M%S").encode()
