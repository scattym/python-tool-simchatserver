import binascii
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

def unpad_byte_string(data):
    for i in range(1, 16):
        found = True
        for j in range(1, i+1):
            if ord(data[-j]) != i:
                found = False

        if found is True:
            return data[0:-i]
    return data

def pad_byte_string(data):
    data_length = len(data)
    print("Length is %s", len(data))
    extra_bytes = data_length % 16
    missing_bytes = 16 - extra_bytes
    print("Missing bytes is %s", missing_bytes)
    for i in range(0,missing_bytes):
        data = data + chr(missing_bytes)
    print("Length is now %s", len(data))
    print(binascii.hexlify(data))
    return data

def decrypt(enc):

    # print binascii.hexlify(bytearray(enc))
    iv = enc[:16]
    iv = binascii.unhexlify("00000000000000000000000000000000")
    sha256 = hashlib.sha256()
    sha256.update("password")
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
    sha256.update("password")
    key = sha256.digest()[0:16]
    # print(sha256.hexdigest())
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # clear = unpad(cipher.decrypt(enc[16:]))
    plain_padded = pad_byte_string(plain)
    encrypted = cipher.encrypt(plain_padded)
    print(binascii.hexlify(encrypted))
    # return binascii.hexlify(encrypted)

    # print("Clear is %s" % clear)
    return encrypted