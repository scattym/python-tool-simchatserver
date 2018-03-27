import datetime
import logging

logger = logging.getLogger(__name__)


class Command(object):
    def __init__(self, direction, payload=None):
        self.payload = payload
        self.direction = direction

    def __repr__(self):
        return self.payload

    def __str__(self):
        return self.payload

    def __getitem__(self, item):
        logger.debug("No implemented on base Command")
        raise AttributeError("No implemented on base Command for field %s" % (item,))

    def __getattr__(self, item):
        logger.debug("No implemented on base Command")
        raise AttributeError("No implemented on base Command for field %s" % (item,))


def meitrack_date_to_datetime(date_time):
    # yymmddHHMMSS
    date_time = "%s%s" % (date_time, "Z")
    d = datetime.datetime.strptime(date_time, "%y%m%d%H%M%SZ")
    return d


def datetime_to_meitrack_date(date_time):
    return date_time.strftime("%y%m%d%H%M%S")
