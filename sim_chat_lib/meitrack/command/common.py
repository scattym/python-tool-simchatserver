import datetime
import logging

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

    def __repr__(self):
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
            return ','.join(fields)
        else:
            return self.payload

    def __getitem__(self, item):
        if item in self.field_dict:
            return self.field_dict[item]
        raise AttributeError("Field %s not set" % (item,))

    def __getattr__(self, item):
        if item in self.field_dict:
            return self.field_dict[item]
        raise AttributeError("Field %s not set" % (item,))

    def parse_payload(self, payload):
        fields = payload.split(',')
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

def meitrack_date_to_datetime(date_time):
    # yymmddHHMMSS
    date_time = "%s%s" % (date_time, "Z")
    d = datetime.datetime.strptime(date_time, "%y%m%d%H%M%SZ")
    return d


def datetime_to_meitrack_date(date_time):
    return date_time.strftime("%y%m%d%H%M%S")
