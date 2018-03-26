import logging
from sim_chat_lib.meitrack.error import GPRSParseError
from sim_chat_lib.meitrack.command.common import Command

logger = logging.getLogger(__name__)


class TrackerCommand(Command):
    field_names = [
        "command", "event_code", "latitude", "longitude", "date_time", "pos_status", "num_sats",
        "gsm_signal_strength", "speed", "direction", "horizontal_accuracy", "altitude", "mileage",
        "run_time", "base_station_info", "io_port_status", "analog_input_value", "assisted_event_info",
        "customized_data", "protocol_version", "fuel_percentage",
        "temp_sensors", "max_acceleration_value", "max_deceleration_value",

    ]
    field_names_50_51 = [
        "command", "event_code", "latitude", "longitude", "date_time", "pos_status", "num_sats",
        "gsm_signal_strength",  "speed", "direction", "horizontal_accuracy", "altitude", "mileage",
        "run_time", "base_station_info", "io_port_status", "analog_input_value",  "assisted_event_info",
        "temperature_sensor_number", "customized_data", "protocol_version", "fuel_percentage",
        "temp_sensors", "max_acceleration_value", "max_deceleration_value",
    ]

    def __init__(self, direction, payload=None):
        super(TrackerCommand, self).__init__(direction, payload=payload)
        self.field_dict = {}
        self.field_name_selector = None
        for field in self.field_names:
            self.field_dict[field] = None

        if payload:
            self.parse_payload(payload)

    def __getitem__(self, item):
        if item in self.field_dict:
            return self.field_dict[item]
        raise AttributeError("Field %s not set" % (item,))

    def parse_payload(self, payload):
        fields = payload.split(',')
        if len(fields) < 2:
            raise GPRSParseError("Field length does not include event code", self.payload)
        if fields[1] in ["50", "51"]:
            self.field_name_selector = self.field_names_50_51
        else:
            self.field_name_selector = self.field_names

        if len(self.field_name_selector) < len(fields):
            print("%s %s" % (len(fields), len(self.field_name_selector)))
            print(payload)
            raise GPRSParseError("Incorrect number of fields for gps data")
        for i in range(0, len(fields)):
            field_name = self.field_name_selector[i]
            self.field_dict[field_name] = fields[i]

    def __str__(self):
        result_str = ""
        result_str = "%s\n" % (self.payload,)
        for field in self.field_names:
            result_str += "\tField %s has value %s\n" % (field, self.field_dict[field])
        return result_str

    def __repr__(self):
        fields = []
        if self.field_name_selector:
            for field in self.field_name_selector:
                if self.field_dict.get(field):
                    fields.append(self.field_dict.get(field))
        if fields is not None:
            return ','.join(fields)
        else:
            return ''


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
        """AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23""",
        """AAA,35,24.819173,121.026060,180323060454,A,8,12,0,24,1.4,60,108,12757,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0984,00000001,,3,,,44,39""",
        """AAA,35,24.819173,121.026053,180323060554,A,8,12,0,189,0.9,59,108,12817,466|97|527B|01036CAB,0000,0000|0000|0000|019D|0983,00000001,,3,,,90,47""",
        """AAA,50,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,,3,,,36,23""",
    ]

    for test in tests:
        test_command = TrackerCommand(test)
        print(repr(test_command))