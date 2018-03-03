import hashlib
import json
import logging

logger = logging.getLogger(__name__)

def command_as_json(type, cmd, key, seed=None):
    config = {
        type: str(cmd.rstrip()),
    }

    sha256 = hashlib.sha256()
    sha256.update(key.encode())
    if seed is not None:
        sha256.update(seed)
    for key in sorted(config):
        logger.debug("Key: %s, value: %s", key, config[key])
        sha256.update(key.encode())
        sha256.update(("%s" % (config[key])).encode())
    sha256.update(key.encode())
    config["checksum"] = sha256.hexdigest()

    return json.dumps(config)


def calc_hash(key, seed, *args):
    sha256 = hashlib.sha256()
    sha256.update(key)
    if seed is not None:
        sha256.update(seed)
    for value in args:
        logger.debug("Value: %s", value)
        sha256.update("%s" % (value,))
    sha256.update(key)

    return sha256.hexdigest()

