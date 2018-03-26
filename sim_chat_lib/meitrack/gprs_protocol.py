#!/usr/bin/env python
import logging

import sys
from sim_chat_lib.meitrack import event
from sim_chat_lib.meitrack.command import command_to_object
from sim_chat_lib.meitrack.error import GPRSParseError

logger = logging.getLogger(__name__)

"""
payload $$<Data identifier><Data length>,<IMEI>,<Command type>,<Command><*Checksum>\r\n
"""
SERVER_TO_CLIENT_PREFIX = '@@'
CLIENT_TO_SERVER_PREFIX = '$$'
END_OF_MESSAGE_STRING = '\r\n'

DIRECTION_SERVER_TO_CLIENT = 0
DIRECTION_CLIENT_TO_SERVER = 1


def prefix_to_direction(prefix):
    if prefix == SERVER_TO_CLIENT_PREFIX:
        return DIRECTION_SERVER_TO_CLIENT
    elif prefix == CLIENT_TO_SERVER_PREFIX:
        return DIRECTION_CLIENT_TO_SERVER
    raise GPRSParseError("Invalid prefix %s" % (prefix,))


class GPRS(object):
    def __init__(self, payload=None):
        self.payload = ""
        self.direction = None
        self.data_identifier = None
        self.data_length = 0
        self.data_payload = None
        self.imei = None
        self.command_type = None
        self.checksum = None
        self.enclosed_data = None
        self.leftover = ""
        if payload:
            self.parse_data_payload(payload)

    def parse_data_payload(self, payload):
        self.payload = payload
        self.direction = payload[0:2]
        self.data_identifier = payload[2]
        self.checksum = payload[-4:-2]
        first_comma = payload.find(',')
        self.data_length = payload[3:first_comma]
        self.data_payload = payload[first_comma:]
        self.leftover = payload[first_comma+1:-5]

        next_comma = self.leftover.find(',')
        self.imei = self.leftover[:next_comma]
        self.leftover = self.leftover[next_comma+1:]

        self.command_type = self.leftover[0:3]
        self.leftover = self.leftover
        self.enclosed_data = command_to_object(
            prefix_to_direction(self.direction),
            self.command_type,
            self.leftover
        )

    @property
    def checksum(self):
        if self.__checksum:
            return self.__checksum
        return "XX"

    @checksum.setter
    def checksum(self, checksum):
        self.__checksum = checksum

    @property
    def enclosed_data(self):
        return self.__enclosed_data

    @enclosed_data.setter
    def enclosed_data(self, enclosed_commmand_object):
        if enclosed_commmand_object is not None:
            self.leftover = repr(enclosed_commmand_object)
            self.__enclosed_data = enclosed_commmand_object

    @property
    def data_length(self):
        data = ",%s,%s*%s%s" % (
            self.imei,
            self.leftover,
            self.checksum,
            END_OF_MESSAGE_STRING
        )
        return len(data)

    @data_length.setter
    def data_length(self, data_length):
        self.__data_length = data_length

    def __str__(self):
        return_str = "Payload: %s\n" % (self.payload,)
        return_str += "Direction: %s\n" % (self.direction,)
        return_str += "identifier: %s\n" % (self.data_identifier,)
        return_str += "length: %s\n" % (self.data_length,)
        return_str += "data payload: %s\n" % (self.data_payload,)
        return_str += "imei: %s\n" % (self.imei,)
        return_str += "command_type: %s\n" % (self.command_type,)
        return_str += "checksum: %s\n" % (self.checksum,)
        return_str += "leftover: %s\n" % (self.leftover,)
        if self.enclosed_data:
            return_str += str(self.enclosed_data)
        return return_str

    def __repr__(self):
        return_str = "%s%s%s,%s,%s*%s%s" % (
            self.direction,
            self.data_identifier,
            self.data_length,
            self.imei,
            self.leftover,
            self.checksum,
            END_OF_MESSAGE_STRING
        )
        return return_str


def parse_data_payload(payload):
    leftover = ""
    before = ""
    gprs_list = []
    while len(payload) > 0:

        direction_start = payload.find(CLIENT_TO_SERVER_PREFIX)
        if direction_start < 0:
            direction_start = payload.find(SERVER_TO_CLIENT_PREFIX)
        if direction_start < 0:
            print(payload)
            raise GPRSParseError("Unable to find start of payload")

        direction_end = direction_start + 2
        if direction_start > 0:
            before = payload[0:direction_start]

        payload = payload[direction_start:]

        data_identifier = payload[2]

        first_comma = payload.find(',')

        data_length = int(payload[3:first_comma])

        if len(payload[first_comma:]) != data_length:
            print(payload)
        message = payload[:first_comma+data_length]
        if message[-2:] != END_OF_MESSAGE_STRING:
            logger.debug("Last two characters of message is >%s<", message[-2:])
            raise GPRSParseError("Found begin token, but length does not lead to end of payload. %s", payload)
        current_gprs = GPRS(message)
        gprs_list.append(current_gprs)

        if len(payload[first_comma:]) > data_length:
            payload = payload[first_comma+data_length:]
        else:
            payload = ""

    return gprs_list, before, leftover


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

    test_data = [
        """$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n""",
        """$$G162,864507032228727,AAA,35,24.818730,121.025900,180323055955,A,5,13,0,250,1.2,65,67,12460,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0980,00000001,,3,,,42,39*49\r\n""",
        """$$L162,864507032228727,AAA,35,24.819173,121.026060,180323060454,A,8,12,0,24,1.4,60,108,12757,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0984,00000001,,3,,,44,39*4D\r\n""",
        """$$M163,864507032228727,AAA,35,24.819173,121.026053,180323060554,A,8,12,0,189,0.9,59,108,12817,466|97|527B|01036CAB,0000,0000|0000|0000|019D|0983,00000001,,3,,,90,47*A4\r\n""",
        """$$N163,864507032228727,AAA,35,24.819116,121.026023,180323060654,A,9,15,0,268,0.9,58,112,12877,466|97|527B|010319B1,0000,0001|0000|0000|019D|0983,00000001,,3,,,35,82*82\r\n""",
        """$$H163,864507032228727,AAA,35,24.819120,121.026041,180323061242,A,7,14,1,200,0.9,58,172,13212,466|97|527B|01035C49,0000,0001|0000|0000|019D|0983,00000001,,3,,,53,84*61\r\n""",
        """$$I163,864507032228727,AAA,35,24.819040,121.026001,180323061342,A,7,14,0,310,0.9,58,180,13272,466|97|527B|01035DB3,0000,0001|0000|0000|019D|0983,00000001,,3,,,50,92*6B\r\n""",
        """$$J163,864507032228727,AAA,35,24.819090,121.026008,180323061441,A,7,14,0,233,0.9,57,184,13331,466|97|527B|01035DB3,0000,0001|0000|0000|019D|0983,00000001,,3,,,38,46*80\r\n""",
        """$$K163,864507032228727,AAA,35,24.819126,121.026058,180323061541,A,8,14,0,149,0.9,57,185,13391,466|97|527B|01035DB4,0000,0001|0000|0000|019D|0984,00000001,,3,,,43,47*94\r\n""",
        """$$S163,864507032228727,AAA,35,24.819118,121.026070,180323062200,A,9,14,0,114,0.8,57,196,13770,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0983,00000001,,3,,,93,73*8C\r\n""",
        """$$T163,864507032228727,AAA,35,24.819118,121.026070,180323062300,A,9,14,0,114,0.8,57,196,13829,466|97|527B|01035DB3,0000,0000|0000|0000|019D|0983,00000001,,3,,,88,44*95\r\n""",
        """@@Q25,353358017784062,A10*6A\r\n""",
        """@@S28,353358017784062,A11,10*FD\r\n""",
        """$$S28,353358017784062,A11,OK*FE\r\n""",
        """@@Q25,353358017784062,A10*6A\r\n""",
        """$$Q128,353358017784062,AAA,34,22.543176,114.078448,100313093738,A,5,22,2,205,5,-14,0,60,0|0|10133|4110,0000,149|153|173|2707|914,*91\r\n""",
        """@@S28,353358017784062,A11,10*FD\r\n""",
        """$$S28,353358017784062,A11,OK*FE\r\n""",
        """@@V27,353358017784062,A12,6*D5\r\n""",
        """$$V28,353358017784062,A12,OK*02\r\n""",
        """@@X29,353358017784062,A13,120*37\r\n""",
        """$$X28,353358017784062,A13,OK*05\r\n""",
        """@@D30,353358017784062,A14,1000*4A\r\n""",
        """$$D28,353358017784062,A14,OK*F2\r\n""",
        """@@E27,353358017784062,A15,6*C7\r\n""",
        """$$E28,353358017784062,A15,OK*F4\r\n""",
        """@@F27,353358017784062,A16,0*C3\r\n""",
        """$$F28,353358017784062,A16,OK*F6\r\n""",
        """@@T27,353358017784062,A17,1*D3\r\n""",
        """$$T28,353358017784062,A17,OK*05\r\n""",
        """@@H27,353358017784062,A19,1*C9\r\n""",
        """$$H28,353358017784062,A19,OK*F8\r\n""",
        """@@H48,353358017784062,A21,1,67.203.13.26,8800,,,*C9\r\n""",
        """$$H28,353358017784062,A21,OK*F4\r\n""",
        """@@K38,353358017784062,A22,75.127.67.90*FD\r\n""",
        """$$K28,353358017784062,A22,OK*F8\r\n""",
        """@@S43,353358017784062,A23,67.203.13.26,8800*F0\r\n""",
        """$$S28,353358017784062,A23,OK*01\r\n""",
        """@@T25,353358017784062,A70*93\r\n""",
        """$$T85,353358017784062,A70,13811111111,13822222222,13833333333,13844444444,13855555555*21\r\n""",
        """@@U61,353358017784062,A71,13811111111,13822222222,13833333333*7D\r\n""",
        """$$U28,353358017784062,A71,OK*06\r\n""",
        """@@V49,353358017784062,A72,13844444444,13855555555*55\r\n""",
        """$$V28,353358017784062,A72,OK*08\r\n""",
        """@@W27,353358017784062,A73,2*D9\r\n""",
        """$$W28,353358017784062,A73,OK*0A\r\n""",
        """@@h27,353358017784062,AFF,1*0B\r\n""",
        """$$h28,353358017784062,AFF,OK*3D\r\n""",
        """@@H57,353358017784062,B05,1,22.913191,114.079882,1000,0,1*96\r\n""",
        """$$H28,353358017784062,B05,OK*F7\r\n""",
        """@@J27,353358017784062,B06,1*C8\r\n""",
        """$$J28,353358017784062,B06,OK*FA\r\n""",
        """@@P28,353358017784062,B07,60*05\r\n""",
        """$$P28,353358017784062,B07,OK*01\r\n""",
        """@@I27,353358017784062,B08,3*CB\r\n""",
        """$$I28,353358017784062,B08,OK*FB\r\n""",
        """@@C27,353358017784062,B21,1*BE\r\n""",
        """$$C28,353358017784062,B21,OK*F0\r\n""",
        """@@J28,353358017784062,B31,10*F7\r\n""",
        """$$J28,353358017784062,B31,OK*F8\r\n""",
        """@@N28,353358017784062,B34,60*03\r\n""",
        """$$N28,353358017784062,B34,OK*FF\r\n""",
        """@@O29,353358017784062,B35,480*3C\r\n""",
        """$$O28,353358017784062,B35,OK*01\r\n""",
        """@@P29,353358017784062,B36,480*3E\r\n""",
        """$$P28,353358017784062,B36,OK*03\r\n""",
        """@@U27,353358017784062,B60,1*D3\r\n""",
        """$$U28,353358017784062,B60,OK*05\r\n""",
        """@@R31,353358017784062,B91,1,SOS*F0\r\n""",
        """$$R28,353358017784062,B91,OK*06\r\n""",
        """@@q42,353358017784062,B92,1234567890ABCDEF*62\r\n""",
        """$$q28,353358017784062,B92,OK*26\r\n""",
        """@@V25,353358017784062,B93*7B\r\n""",
        """$$V42,353358017784062,B93,00000007E01C001F*B5\r\n""",
        """@@A42,353358017784062,B96,0000000000000001*95\r\n""",
        """$$A28,353358017784062,B96,OK*FA\r\n""",
        """@@C25,353358017784062,B97*6C\r\n""",
        """$$C42,353358017784062,B97,0000000000000001*60\r\n""",
        """@@B34,863070010825791,B99,gprs,get*BC\r\n""",
        """$$B33,863070010825791,B99,1,17,18*B5\r\n""",
        """@@M34,353358017784062,C01,20,10122*18\r\n""",
        """$$M28,353358017784062,C01,OK*F9\r\n""",
        # """@@f47,353358017784062,C02,0,15360853789,Meitrack*B1\r\n""",
        """@@f47,353358017784062,C02,0,15360853789,Meitrac*B1\r\n""",
        """$$f28,353358017784062,C02,OK*13\r\n""",
        """@@f27,353358017784062,C03,0*E1\r\n""",
        """$$f28,353358017784062,C03,OK*14\r\n""",
        """@@m42,013777001338688,C13,0,E,TestMessage*08\r\n""",
        """$$m28,013777001338688,C13,OK*1C\r\n""",
        # """@@q35,012896001078259,C40,(1BD5#040000W02*50\r\n""",
        # """$$q36,012896001078259,C40,(1BD5#040000W0201*1B\r\n""",
        """@@n28,012896001078259,C41,01*19\r\n""",
        """$$n30,012896001078259,C41,01,1*37\r\n""",
        """@@m25,012896001078259,C42*89\r\n""",
        # """$$t45,012896001078259,C42,(B4v#040000R00,(1BD5#040000W00*13\r\n""",
        # """@@o57,012896001078259,C43,01(1BD5#040000W<0005000101T1#00000000000000000000000000*3F""",
        # """$$o28,012896001078259,C43,0101*85\r\n""",
        """$$o32,012896001078259,C43,0101*85\r\n""",
        """@@r25,012896001078259,C44*90\r\n""",
        # """$$r274,012896001078259,C44,01(B4v#040000R0000000000000000000000000000000000000000000002(1BD5#040000W00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000*1E\r\n""",
        """@@i25,012896001078259,C46*89\r\n""",
        # """$$i28,012896001078259,C46,12_*F1\r\n""",
        """$$i28,012896001078259,C46,12*F1\r\n""",
        """@@f33,353358017784062,C47,2,90,10*0A\r\n""",
        """$$f28,353358017784062,C47,OK*1C\r\n""",
        """@@c25,353358017784062,C48*89\r\n""",
        """$$c33,353358017784062,C48,2,90,10*D0\r\n""",
        """@@c29,353358017784062,C49,3,2*4B\r\n""",
        """$$c28,353358017784062,C49,ok*5B\r\n""",
        """@@O48,353358017784062,D00,0215080432_C2E03.jpg,0*DB\r\n""",
        """@@A27,353358017784062,D01,0*BB\r\n""",
        """$$A480,353358017784062,D01,3,0,0506162517_C1E03.jpg|0506162517_C1E11.jpg|0506162624_C1E03.jpg|0506162630_C1E11.jpg|0506162720_C1E03.jpg|0506162721_C1E03.jpg|0215080547_C1E03.jpg|0215080547_C1E11.jpg|0215080626_C1E03.jpg|0215080626_C1E11.jpg|0215080827_C1E03.jpg|0215080827_C1E11.jpg|0215080850_C1E03.jpg|0215080850_C1E11.jpg|0507145426_C1E03.jpg|0507145426_C1E11.jpg|0507145512_C2E03.jpg|0507145512_C2E11.jpg|0215080050_C3E03.jpg|0215080050_C3E11.jpg|0215080459_C3E03.jpg|021508050*41\r\n""",
        """@@E110,353358017784062,D02,0506162517_C1E03.jpg|0506162517_C1E11.jpg|0506162624_C1E03.jpg|0506162630_C1E11.jpg|*4E\r\n""",
        """$$F28,353358017784062,D02,OK*F4\r\n""",
        """@@D46,353358017784062,D03,1,camerapicture.jpg*E2\r\n""",
        """$$D28,353358017784062,D03,OK*F3\r\n""",
        """@@f43,353358017784062,D10,13737431,13737461*17\r\n""",
        """$$f28,353358017784062,D10,OK*13\r\n""",
        """@@e36,353358017784062,D11,13737431,1*AA\r\n""",
        """$$e28,353358017784062,D11,OK*13\r\n""",
        """@@C34,353358017784062,D12,13737431*2A\r\n""",
        """$$C27,353358017784062,D12,0*87\r\n""",
        """@@w27,353358017784062,D13,0*F4\r\n""",
        """@@Q34,353358017784062,D14,13723455*3B\r\n""",
        """$$Q28,353358017784062,D14,OK*02\r\n""",
        """@@K36,353358017784062,D15,13723455,3*97\r\n""",
        """$$K28,353358017784062,D15,OK*FD\r\n""",
        """@@u25,353358017784062,D16*97\r\n""",
        """$$u28,353358017784062,D16,18*F7\r\n""",
        """@@V75,353358017784062,D65,30000,50000,60000,70000,80000,90000,100000,110000*EA\r\n""",
        """$$V28,353358017784062,D65,OK*OD\r\n""",
        """@@V65,353358017784062,D66,8726,8816,8906,8996,9086,9176,9266,9356*A2\r\n""",
        """$$V28,353358017784062,D66OK*E2\r\n""",
        """@@W25,353358017784062,E91*7D\r\n""",
        """$$W38,353358017784062,FWV1.00,12345678*1C\r\n""",
        """@@j25,353358017784062,F01*88\r\n""",
        """$$j28,353358017784062,F01,OK*19\r\n""",
        """@@Z25,353358017784062,F02*79\r\n""",
        """$$Z28,353358017784062,F02,OK*0A\r\n""",
        """@@D40,353358017784062,F08,0,4825000*51\r\n""",
        """$$D28,353358017784062,F08,OK*FA\r\n""",
        """@@E27,353358017784062,F09,1*CA\r\n""",
        """$$E28,353358017784062,F09,OK*FC\r\n""",
        """@@[25,353358017784062,F11*7A\r\n""",
        """$$[28,353358017784062,F11,OK*0B\r\n""",
        """$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n""",
        """$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n"""
        """$$D161,864507032228727,AAA,50,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,,3,,,36,23*DC\r\n""",
    ]
    for gprs_item in test_data:
        test_gprs_list, before_bytes, extra_bytes = parse_data_payload(gprs_item)
        for gprs in test_gprs_list:
            print(gprs)
        if before_bytes:
            print("Before bytes is ", before_bytes)
        if extra_bytes:
            print("Leftover is ", extra_bytes)
