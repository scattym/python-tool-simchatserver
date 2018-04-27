#!/usr/bin/env python
import logging

import sys
from sim_chat_lib.meitrack import event
from sim_chat_lib.meitrack.command import command_to_object
from sim_chat_lib.meitrack.error import GPRSParseError
from sim_chat_lib.meitrack.common import CLIENT_TO_SERVER_PREFIX, SERVER_TO_CLIENT_PREFIX, DIRECTION_CLIENT_TO_SERVER
from sim_chat_lib.meitrack.common import DIRECTION_SERVER_TO_CLIENT, END_OF_MESSAGE_STRING


logger = logging.getLogger(__name__)

"""
payload $$<Data identifier><Data length>,<IMEI>,<Command type>,<Command><*Checksum>\r\n
"""


def prefix_to_direction(prefix):
    if prefix == SERVER_TO_CLIENT_PREFIX:
        return DIRECTION_SERVER_TO_CLIENT
    elif prefix == CLIENT_TO_SERVER_PREFIX:
        return DIRECTION_CLIENT_TO_SERVER
    raise GPRSParseError("Invalid prefix %s" % (prefix,))


class GPRS(object):
    def __init__(self, payload=None):
        self.payload = b""
        self.direction = None
        self.data_identifier = None
        self.data_length = b"0"
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
        self.data_identifier = chr(payload[2]).encode()
        self.checksum = payload[-4:-2]
        first_comma = payload.find(b',')
        # print("Data length is")
        # print(payload[3:first_comma])
        # print(type(payload[3:first_comma]))
        self.data_length = payload[3:first_comma]
        self.data_payload = payload[first_comma:]
        self.leftover = payload[first_comma+1:-5]

        next_comma = self.leftover.find(b',')
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
        return b"XX"

    @checksum.setter
    def checksum(self, checksum):
        self.__checksum = checksum

    @property
    def enclosed_data(self):
        return self.__enclosed_data

    @enclosed_data.setter
    def enclosed_data(self, enclosed_commmand_object):
        if enclosed_commmand_object is not None:
            self.leftover = enclosed_commmand_object.as_bytes()
            self.__enclosed_data = enclosed_commmand_object

    @property
    def data_length(self):
        data = (
                b"," + self.imei + b"," +
                self.leftover + b"*" + self.checksum + END_OF_MESSAGE_STRING
        )
        return str(len(data)).encode()

    @data_length.setter
    def data_length(self, data_length):
        self.__data_length = str(data_length).encode()

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

    def as_bytes(self):
        # print(chr(self.data_identifier).encode())
        # print(type(chr(self.data_identifier).encode()))
        # print(self.data_length)
        string_to_sign = (
                self.direction + self.data_identifier + self.data_length
                + b"," + self.imei + b"," + self.leftover + b"*"
        )
        checksum_hex = "{:02X}".format(calc_signature(string_to_sign))
        self.checksum = checksum_hex.encode()
        # self.checksum = "{:02X}".format(calc_signature(string_to_sign))
        # print(type(self.data_identifier))
        return_str = (
                self.direction + self.data_identifier + self.data_length
                + b"," + self.imei + b"," +
                 self.leftover + b"*" + self.checksum + END_OF_MESSAGE_STRING
        )
        # print("RETURN STRING")
        # print(return_str)
        # return_str = "%s%s%s,%s,%s*%s%s" % (
        #     self.direction,
        #     self.data_identifier,
        #     self.data_length,
        #     self.imei,
        #     self.leftover,
        #     self.checksum,
        #     END_OF_MESSAGE_STRING
        # )
        return return_str


def parse_data_payload(payload):
    leftover = b''
    before = b''
    gprs_list = []
    while len(payload) > 0:

        direction_start = payload.find(CLIENT_TO_SERVER_PREFIX)
        if direction_start < 0:
            direction_start = payload.find(SERVER_TO_CLIENT_PREFIX)
        if direction_start < 0:
            logger.error("Unable to find start payload")
            leftover = payload
            payload = b''
        else:
            direction_end = direction_start + 2
            if direction_start > 0:
                before = payload[0:direction_start]

            payload = payload[direction_start:]

            data_identifier = payload[2]

            first_comma = payload.find(b',')
            if not first_comma:
                logger.error("No first comma found. Can't get to calculate length of payload")
                leftover = payload
                payload = b''
            else:
                logger.debug("Data length is %s", payload[3:first_comma])
                data_length = int(payload[3:first_comma])

                if len(payload) >= (first_comma + data_length):
                    logger.debug("Start of payload is {}".format(payload[0:2]))
                    logger.debug("End of payload is {}".format(payload[-2:]))
                    message = payload[:first_comma+data_length]
                    payload = payload[first_comma+data_length:]

                    if message[-2:] != END_OF_MESSAGE_STRING:
                        logger.error("Last two characters of message is >%s<", message[-2:])
                        raise GPRSParseError("Found begin token, but length does not lead to end of payload. %s", payload)

                    current_gprs = GPRS(message)
                    gprs_list.append(current_gprs)
                else:
                    leftover = payload
                    payload = b''

    return gprs_list, before, leftover


def calc_signature(payload):
    # print(type(payload))
    # print(payload)
    checksum = 0
    lastchar = payload.find(b'*')
    for char in payload[0:lastchar+1]:
        checksum = checksum + char
    checksum = checksum & 0xFF
    # print("checksum is ", checksum)
    return checksum

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
        b"""$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n""",
        b"""$$G162,864507032228727,AAA,35,24.818730,121.025900,180323055955,A,5,13,0,250,1.2,65,67,12460,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0980,00000001,,3,,,42,39*49\r\n""",
        b"""$$L162,864507032228727,AAA,35,24.819173,121.026060,180323060454,A,8,12,0,24,1.4,60,108,12757,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0984,00000001,,3,,,44,39*4D\r\n""",
        b"""$$M163,864507032228727,AAA,35,24.819173,121.026053,180323060554,A,8,12,0,189,0.9,59,108,12817,466|97|527B|01036CAB,0000,0000|0000|0000|019D|0983,00000001,,3,,,90,47*A4\r\n""",
        b"""$$N163,864507032228727,AAA,35,24.819116,121.026023,180323060654,A,9,15,0,268,0.9,58,112,12877,466|97|527B|010319B1,0000,0001|0000|0000|019D|0983,00000001,,3,,,35,82*82\r\n""",
        b"""$$H163,864507032228727,AAA,35,24.819120,121.026041,180323061242,A,7,14,1,200,0.9,58,172,13212,466|97|527B|01035C49,0000,0001|0000|0000|019D|0983,00000001,,3,,,53,84*61\r\n""",
        b"""$$I163,864507032228727,AAA,35,24.819040,121.026001,180323061342,A,7,14,0,310,0.9,58,180,13272,466|97|527B|01035DB3,0000,0001|0000|0000|019D|0983,00000001,,3,,,50,92*6B\r\n""",
        b"""$$J163,864507032228727,AAA,35,24.819090,121.026008,180323061441,A,7,14,0,233,0.9,57,184,13331,466|97|527B|01035DB3,0000,0001|0000|0000|019D|0983,00000001,,3,,,38,46*80\r\n""",
        b"""$$K163,864507032228727,AAA,35,24.819126,121.026058,180323061541,A,8,14,0,149,0.9,57,185,13391,466|97|527B|01035DB4,0000,0001|0000|0000|019D|0984,00000001,,3,,,43,47*94\r\n""",
        b"""$$S163,864507032228727,AAA,35,24.819118,121.026070,180323062200,A,9,14,0,114,0.8,57,196,13770,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0983,00000001,,3,,,93,73*8C\r\n""",
        b"""$$T163,864507032228727,AAA,35,24.819118,121.026070,180323062300,A,9,14,0,114,0.8,57,196,13829,466|97|527B|01035DB3,0000,0000|0000|0000|019D|0983,00000001,,3,,,88,44*95\r\n""",
        b"""@@Q25,353358017784062,A10*6A\r\n""",
        b"""@@S28,353358017784062,A11,10*FD\r\n""",
        b"""$$S28,353358017784062,A11,OK*FE\r\n""",
        b"""@@Q25,353358017784062,A10*6A\r\n""",
        b"""$$Q128,353358017784062,AAA,34,22.543176,114.078448,100313093738,A,5,22,2,205,5,-14,0,60,0|0|10133|4110,0000,149|153|173|2707|914,*91\r\n""",
        b"""@@S28,353358017784062,A11,10*FD\r\n""",
        b"""$$S28,353358017784062,A11,OK*FE\r\n""",
        b"""@@V27,353358017784062,A12,6*D5\r\n""",
        b"""$$V28,353358017784062,A12,OK*02\r\n""",
        b"""@@X29,353358017784062,A13,120*37\r\n""",
        b"""$$X28,353358017784062,A13,OK*05\r\n""",
        b"""@@D30,353358017784062,A14,1000*4A\r\n""",
        b"""$$D28,353358017784062,A14,OK*F2\r\n""",
        b"""@@E27,353358017784062,A15,6*C7\r\n""",
        b"""$$E28,353358017784062,A15,OK*F4\r\n""",
        b"""@@F27,353358017784062,A16,0*C3\r\n""",
        b"""$$F28,353358017784062,A16,OK*F6\r\n""",
        b"""@@T27,353358017784062,A17,1*D3\r\n""",
        b"""$$T28,353358017784062,A17,OK*05\r\n""",
        b"""@@H27,353358017784062,A19,1*C9\r\n""",
        b"""$$H28,353358017784062,A19,OK*F8\r\n""",
        b"""@@H48,353358017784062,A21,1,67.203.13.26,8800,,,*C9\r\n""",
        b"""$$H28,353358017784062,A21,OK*F4\r\n""",
        b"""@@K38,353358017784062,A22,75.127.67.90*FD\r\n""",
        b"""$$K28,353358017784062,A22,OK*F8\r\n""",
        b"""@@S43,353358017784062,A23,67.203.13.26,8800*F0\r\n""",
        b"""$$S28,353358017784062,A23,OK*01\r\n""",
        b"""@@T25,353358017784062,A70*93\r\n""",
        b"""$$T85,353358017784062,A70,13811111111,13822222222,13833333333,13844444444,13855555555*21\r\n""",
        b"""@@U61,353358017784062,A71,13811111111,13822222222,13833333333*7D\r\n""",
        b"""$$U28,353358017784062,A71,OK*06\r\n""",
        b"""@@V49,353358017784062,A72,13844444444,13855555555*55\r\n""",
        b"""$$V28,353358017784062,A72,OK*08\r\n""",
        b"""@@W27,353358017784062,A73,2*D9\r\n""",
        b"""$$W28,353358017784062,A73,OK*0A\r\n""",
        b"""@@h27,353358017784062,AFF,1*0B\r\n""",
        b"""$$h28,353358017784062,AFF,OK*3D\r\n""",
        b"""@@H57,353358017784062,B05,1,22.913191,114.079882,1000,0,1*96\r\n""",
        b"""$$H28,353358017784062,B05,OK*F7\r\n""",
        b"""@@J27,353358017784062,B06,1*C8\r\n""",
        b"""$$J28,353358017784062,B06,OK*FA\r\n""",
        b"""@@P28,353358017784062,B07,60*05\r\n""",
        b"""$$P28,353358017784062,B07,OK*01\r\n""",
        b"""@@I27,353358017784062,B08,3*CB\r\n""",
        b"""$$I28,353358017784062,B08,OK*FB\r\n""",
        b"""@@C27,353358017784062,B21,1*BE\r\n""",
        b"""$$C28,353358017784062,B21,OK*F0\r\n""",
        b"""@@J28,353358017784062,B31,10*F7\r\n""",
        b"""$$J28,353358017784062,B31,OK*F8\r\n""",
        b"""@@N28,353358017784062,B34,60*03\r\n""",
        b"""$$N28,353358017784062,B34,OK*FF\r\n""",
        b"""@@O29,353358017784062,B35,480*3C\r\n""",
        b"""$$O28,353358017784062,B35,OK*01\r\n""",
        b"""@@P29,353358017784062,B36,480*3E\r\n""",
        b"""$$P28,353358017784062,B36,OK*03\r\n""",
        b"""@@U27,353358017784062,B60,1*D3\r\n""",
        b"""$$U28,353358017784062,B60,OK*05\r\n""",
        b"""@@R31,353358017784062,B91,1,SOS*F0\r\n""",
        b"""$$R28,353358017784062,B91,OK*06\r\n""",
        b"""@@q42,353358017784062,B92,1234567890ABCDEF*62\r\n""",
        b"""$$q28,353358017784062,B92,OK*26\r\n""",
        b"""@@V25,353358017784062,B93*7B\r\n""",
        b"""$$V42,353358017784062,B93,00000007E01C001F*B5\r\n""",
        b"""@@A42,353358017784062,B96,0000000000000001*95\r\n""",
        b"""$$A28,353358017784062,B96,OK*FA\r\n""",
        b"""@@C25,353358017784062,B97*6C\r\n""",
        b"""$$C42,353358017784062,B97,0000000000000001*60\r\n""",
        b"""@@B34,863070010825791,B99,gprs,get*BC\r\n""",
        b"""$$B33,863070010825791,B99,1,17,18*B5\r\n""",
        b"""@@M34,353358017784062,C01,20,10122*18\r\n""",
        b"""$$M28,353358017784062,C01,OK*F9\r\n""",
        # b"""@@f47,353358017784062,C02,0,15360853789,Meitrack*B1\r\n""",
        b"""@@f47,353358017784062,C02,0,15360853789,Meitrac*B1\r\n""",
        b"""$$f28,353358017784062,C02,OK*13\r\n""",
        b"""@@f27,353358017784062,C03,0*E1\r\n""",
        b"""$$f28,353358017784062,C03,OK*14\r\n""",
        b"""@@m42,013777001338688,C13,0,E,TestMessage*08\r\n""",
        b"""$$m28,013777001338688,C13,OK*1C\r\n""",
        # b"""@@q35,012896001078259,C40,(1BD5#040000W02*50\r\n""",
        # b"""$$q36,012896001078259,C40,(1BD5#040000W0201*1B\r\n""",
        b"""@@n28,012896001078259,C41,01*19\r\n""",
        b"""$$n30,012896001078259,C41,01,1*37\r\n""",
        b"""@@m25,012896001078259,C42*89\r\n""",
        # b"""$$t45,012896001078259,C42,(B4v#040000R00,(1BD5#040000W00*13\r\n""",
        # b"""@@o57,012896001078259,C43,01(1BD5#040000W<0005000101T1#00000000000000000000000000*3F""",
        # b"""$$o28,012896001078259,C43,0101*85\r\n""",
        b"""$$o32,012896001078259,C43,0101*85\r\n""",
        b"""@@r25,012896001078259,C44*90\r\n""",
        # b"""$$r274,012896001078259,C44,01(B4v#040000R0000000000000000000000000000000000000000000002(1BD5#040000W00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000*1E\r\n""",
        b"""@@i25,012896001078259,C46*89\r\n""",
        # b"""$$i28,012896001078259,C46,12_*F1\r\n""",
        b"""$$i28,012896001078259,C46,12*F1\r\n""",
        b"""@@f33,353358017784062,C47,2,90,10*0A\r\n""",
        b"""$$f28,353358017784062,C47,OK*1C\r\n""",
        b"""@@c25,353358017784062,C48*89\r\n""",
        b"""$$c33,353358017784062,C48,2,90,10*D0\r\n""",
        b"""@@c29,353358017784062,C49,3,2*4B\r\n""",
        b"""$$c28,353358017784062,C49,ok*5B\r\n""",
        b"""@@O48,353358017784062,D00,0215080432_C2E03.jpg,0*DB\r\n""",
        b"""@@A27,353358017784062,D01,0*BB\r\n""",
        b"""$$A480,353358017784062,D01,3,0,0506162517_C1E03.jpg|0506162517_C1E11.jpg|0506162624_C1E03.jpg|0506162630_C1E11.jpg|0506162720_C1E03.jpg|0506162721_C1E03.jpg|0215080547_C1E03.jpg|0215080547_C1E11.jpg|0215080626_C1E03.jpg|0215080626_C1E11.jpg|0215080827_C1E03.jpg|0215080827_C1E11.jpg|0215080850_C1E03.jpg|0215080850_C1E11.jpg|0507145426_C1E03.jpg|0507145426_C1E11.jpg|0507145512_C2E03.jpg|0507145512_C2E11.jpg|0215080050_C3E03.jpg|0215080050_C3E11.jpg|0215080459_C3E03.jpg|021508050*41\r\n""",
        b"""@@E110,353358017784062,D02,0506162517_C1E03.jpg|0506162517_C1E11.jpg|0506162624_C1E03.jpg|0506162630_C1E11.jpg|*4E\r\n""",
        b"""$$F28,353358017784062,D02,OK*F4\r\n""",
        b"""@@D46,353358017784062,D03,1,camerapicture.jpg*E2\r\n""",
        b"""$$D28,353358017784062,D03,OK*F3\r\n""",
        b"""@@f43,353358017784062,D10,13737431,13737461*17\r\n""",
        b"""$$f28,353358017784062,D10,OK*13\r\n""",
        b"""@@e36,353358017784062,D11,13737431,1*AA\r\n""",
        b"""$$e28,353358017784062,D11,OK*13\r\n""",
        b"""@@C34,353358017784062,D12,13737431*2A\r\n""",
        b"""$$C27,353358017784062,D12,0*87\r\n""",
        b"""@@w27,353358017784062,D13,0*F4\r\n""",
        b"""@@Q34,353358017784062,D14,13723455*3B\r\n""",
        b"""$$Q28,353358017784062,D14,OK*02\r\n""",
        b"""@@K36,353358017784062,D15,13723455,3*97\r\n""",
        b"""$$K28,353358017784062,D15,OK*FD\r\n""",
        b"""@@u25,353358017784062,D16*97\r\n""",
        b"""$$u28,353358017784062,D16,18*F7\r\n""",
        b"""@@V75,353358017784062,D65,30000,50000,60000,70000,80000,90000,100000,110000*EA\r\n""",
        b"""$$V28,353358017784062,D65,OK*OD\r\n""",
        b"""@@V65,353358017784062,D66,8726,8816,8906,8996,9086,9176,9266,9356*A2\r\n""",
        b"""$$V28,353358017784062,D66OK*E2\r\n""",
        b"""@@W25,353358017784062,E91*7D\r\n""",
        b"""$$W38,353358017784062,FWV1.00,12345678*1C\r\n""",
        b"""@@j25,353358017784062,F01*88\r\n""",
        b"""$$j28,353358017784062,F01,OK*19\r\n""",
        b"""@@Z25,353358017784062,F02*79\r\n""",
        b"""$$Z28,353358017784062,F02,OK*0A\r\n""",
        b"""@@D40,353358017784062,F08,0,4825000*51\r\n""",
        b"""$$D28,353358017784062,F08,OK*FA\r\n""",
        b"""@@E27,353358017784062,F09,1*CA\r\n""",
        b"""$$E28,353358017784062,F09,OK*FC\r\n""",
        b"""@@[25,353358017784062,F11*7A\r\n""",
        b"""$$[28,353358017784062,F11,OK*0B\r\n""",
        b"""$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n""",
        b"""$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n"""
        b"""$$D161,864507032228727,AAA,50,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,,3,,,36,23*DC\r\n""",
#       b"""$$`164,864507032228727,AAA,35,24.818910,121.025936,180329052345,A,7,13,0,16,1.2,69,2720,86125,466|97|527B|01035DB4,0000,0001|0000|0000|019E|097F,00000001,,3,,,124,96*F2""",
        b"""$$A182,864507032323403,AAA,29,-33.815820,151.200085,180424172103,A,6,9,1,0,1.2,68,2450,7931,0|0|0000|00000000,0000,0000|0000|0000|0167|0000,,,108,0000,,3,0,,0|0000|0000|0000|0000|0000*C9\r\n""",
        b"""@@X27,864507032323403,D01,0*C6\r\n""",
        b"""@@A27,353358017784062,D01,0*BB\r\n""",
        b'$$n1084,864507032323403,D00,180425071619_C1E1_N2U1D1.jpg,16,0,\xff\xd8\xff\xdb\x00\x84\x00\x14\x0e\x0f\x12\x0f\r\x14\x12\x10\x12\x17\x15\x14\x18\x1e2!\x1e\x1c\x1c\x1e=,.$2I@LKG@FEPZsbPUmVEFd\x88emw{\x81\x82\x81N`\x8d\x97\x8c}\x96s~\x81|\x01\x15\x17\x17\x1e\x1a\x1e;!!;|SFS||||||||||||||||||||||||||||||||||||||||||||||||||\xff\xc0\x00\x11\x08\x01\xe0\x02\x80\x03\x01!\x00\x02\x11\x01\x03\x11\x01\xff\xdd\x00\x04\x00\n\xff\xc4\x01\xa2\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00e(\xaf\x1c\xb0\xa5\xa0\x02\x8a\x00Z1@\x06*\x1b\x8b8.\x93l\xa82:8\x1c\x8a\xa8\xc9\xc5\xdd\t\x98w\xba|\xb6m\x93\xf3\xc4y\x0e==\xea\xa5z1\x92\x92\xba$)*\x80)h\x01(\xc5\x00-%\x00\x7f\xff\xd0\xe4E\x15\x00-\x14\x00\x84Sh\x00\xa2\x98\tOW#\x83\xc8\xa2\xd7\x01\xdb\x81\xef\xf8S\t\xc9\xa4\x90\tE0\n(\x00\xa2\x80\n\x96\x0b\x89m\xdft.T\xf7\x19\xe0\xd2j\xfa\x01\xff\xd1\xad\xa7k\ts\x84\x98\x85\x93\xdf\x8c\xd6\x9e{\x8e\x95\xc38\xf2\xb1\x05\x15\x00-\x14\x00QL\x02\x8a`\x14P\x00Fj\xb5\xc5\xaa\xc8:\n@a\xddZ\x18\xdb\x81\xc1\xf4\xaaD\x159\x07\x07\xda\xbab\xee\x80\xbbivA\x01\xcf\xe7Z\x91\xbf\x1cv\xaez\x91\xb3\x1989\x14t\xa1\x12\xcf\xff\xd2\x90\x1a\x92\xb8I\x1c\xb4\xa6\x90\r\xa5\x14\x00Q@\tE0\n\x01\xa0\x05\xa0\x9a@%(\xa0\x05\xcd <\xd0\x00i\x01\xc5\x00\x7f\xff\xd3m\x02\xbcr\xc5\xa2\x80\x16\x97\x14\x00b\x8cP\x02\xe2\x8cP\x01\xd8\x82\x01\x07\xa8=\re\xdeh\xca\xc1\x9e\xcf!\x87>Y\xe8}\x85kJ\xa7#\x131\x99J6\xd7R\xad\xe8F)\xb5\xdeHQL\x02\x8a\x00(\xa0\x0f\xff\xd4\xe4\xa8\xa8\x00\xa2\x90\x054\xd3@%\x14\xc0J)\x80\xb4R\x01)h\x00\xa2\x80\n(\x00\xa2\x80?\xff\xd5\xe3\xfb\xe4u\x15\xb1\xa6\xeb-\x19\x11\\\x9c\xaff\xac\xa7\x1ed#\xa0\x8eE\x957FA\x1e\xd4\xfa\xe4\x00\xa2\x80\n(\x00\xa2\x80\nZ\x00)(\x02\xbd\xc5\xba\xc8\xa7\x8a\xc3\xbb\xb41\x92W\xa5\\%g`(\x90T\xf1W\xad.\xcfF=\xebY\xc7*1D\r\n'
    ]
    for gprs_item in test_data:
        test_gprs_list, before_bytes, extra_bytes = parse_data_payload(gprs_item)
        for gprs in test_gprs_list:
            print(gprs)
        if before_bytes:
            print("Before bytes is ", before_bytes)
        if extra_bytes:
            print("Leftover is ", extra_bytes)
        if b"AAA" in gprs_item:
            print(gprs.enclosed_data["longitude"])
            print(gprs.enclosed_data.longitude)

        print(hex(calc_signature(gprs_item)))
