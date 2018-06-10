#!/usr/bin/env python
# chat_client.py
import sys
import socket
import os
# import select
import time

SCS_HOST = os.environ.get("SCS_HOST", 'localhost')
SCS_PORT = int(os.environ.get("SCS_PORT", '65533'))


def encode_message(message):
    try:
        return message.encode()
    except AttributeError as err:
        return message


def send_take_photo_by_imei(imei):
    message = "imei-{},take_photo".format(imei)
    return send_message(message)


def send_photo_list_by_imei(imei):
    message = "imei-{},photo_list".format(imei)
    return send_message(message)


def send_firmware_update(imei):
    message = "imei-{},firmware_update".format(imei)
    return send_message(message)


def send_cancel_firmware_update(imei):
    message = "imei-{},cancel_firmware_update".format(imei)
    return send_message(message)


def send_message(message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        # connect to remote host
        try:
            sock.connect((SCS_HOST, SCS_PORT))
            sock.send("M@ST#R:".encode())
        except Exception as err:
            print('Unable to connect with error: {}'.format(err))
            return False

        print('Connected to remote host. You can start sending messages')
        # time.sleep(1)
        sock.send(message.encode())
        sock.send(b'\n')
        return True
    except Exception as err:
        print("Exception in sending message to server: {}".format(err))
    finally:
        sock.close()
    return False


if __name__ == "__main__":
    sys.exit(send_message('localhost', '65533', 'bc,take_photo'))