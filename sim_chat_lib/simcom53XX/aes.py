import binascii
import hashlib
import logging

logger = logging.getLogger(__name__)

from Crypto import Random
from Crypto.Cipher import AES


def unpad_byte_string(data):
    byte_converter = lambda x : x
    if isinstance(data, str):
        byte_converter = lambda x : ord(x)

    for i in range(1, 16):
        found = True
        for j in range(1, i+1):
            if byte_converter(data[-j]) != i:
                found = False

        if found is True:
            return data[0:-i]

    return data


def pad_byte_string(data):
    data_length = len(data)
    logger.debug("Length is %s", len(data))
    extra_bytes = data_length % 16
    missing_bytes = 16 - extra_bytes
    logger.debug("Missing bytes is %s", missing_bytes)
    for i in range(0, missing_bytes):
        data = data + chr(missing_bytes)
    logger.debug("Length is now %s", len(data))
    logger.debug(binascii.hexlify(data.encode()))
    return data


def decrypt(enc):

    # print binascii.hexlify(bytearray(enc))
    iv = enc[:16]
    iv = binascii.unhexlify("00000000000000000000000000000000")
    sha256 = hashlib.sha256()
    sha256.update("password".encode())
    key = sha256.digest()[0:16]
    # print(sha256.hexdigest())
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # clear = unpad(cipher.decrypt(enc[16:]))
    clear = unpad_byte_string(cipher.decrypt(enc))
    binascii.hexlify(bytearray(clear))
    # print("Clear is %s" % clear)
    return clear.decode('utf8')


def encrypt(plain):

    # print binascii.hexlify(bytearray(enc))
    # iv = enc[:16]
    iv = binascii.unhexlify("00000000000000000000000000000000")
    sha256 = hashlib.sha256()
    sha256.update("password".encode())
    key = sha256.digest()[0:16]
    # print(sha256.hexdigest())
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # clear = unpad(cipher.decrypt(enc[16:]))
    plain_padded = pad_byte_string(plain)
    logger.debug(plain)
    encrypted = cipher.encrypt(plain_padded)
    print(binascii.hexlify(encrypted))
    # return binascii.hexlify(encrypted)

    # print("Clear is %s" % clear)
    return encrypted

# Authorization: bc733796ca38178dbee79f68ba4271e97fe170d4
# Key: 00F9F3B67E14DF4F31511CD15E46B20C1C53EB29AB77FA31DB901DDF7E9279DE
# Version: base
# V: base
# I: 863789027326838
# C: 79.218
# Content-Length: 528
# User-Agent: SimCom/1.0
# Connection: close
# Age: 2.7
# Imei: 863789027326838
# Host: services.pts.scattym.com
# Accept: text/html
# Encrypted: true
# Content-Type: application/octet-stream
# Seed: 4145B41ADA8EFD20531E0E7DC28CF52E


def seed_to_key(seed, imei, version, clock):
    sha256 = hashlib.sha256()
    sha256.update(seed.encode())
    sha256.update(imei.encode())
    sha256.update(version.encode())
    sha256.update(clock.encode())
    key = sha256.digest()[0:16]
    return key


if __name__ == '__main__':
    from timeit import timeit
    log_level = 11 - 2

    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    print(binascii.hexlify(seed_to_key("4145B41ADA8EFD20531E0E7DC28CF52E", "863789027326838", "base", "79.218")))