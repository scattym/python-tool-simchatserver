import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def command_as_json(cmd_type, cmd, hash_key, seed=None):

    config = {
        cmd_type: str(cmd.rstrip()),
    }

    try:
        hash_key = hash_key.encode()
    except AttributeError as _:
        pass
    sha256 = hashlib.sha256()
    sha256.update(hash_key)
    if seed is not None:
        sha256.update(seed)
    for key in sorted(config):
        try:
            key = key.encode()
        except AttributeError as _:
            pass
        logger.log(13, "Key: %s, value: %s", key, config[key])
        sha256.update(key)
        try:
            sha256.update(("%s" % (config[key])).encode())
        except AttributeError as _:
            sha256.update(("%s" % (config[key])))
    sha256.update(hash_key)
    config["checksum"] = sha256.hexdigest()

    return json.dumps(config)


def calc_hash(key, seed, *args):
    try:
        key = key.encode()
    except AttributeError as _:
        pass
    try:
        seed = seed.encode()
    except AttributeError as _:
        pass
    sha256 = hashlib.sha256()
    sha256.update(key)
    if seed is not None:
        sha256.update(seed)
    for value in args:
        logger.log(13, "Value: %s", value)
        sha256.update(("%s" % (value,)).encode())
    sha256.update(key)

    return sha256.hexdigest()

