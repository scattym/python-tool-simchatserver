import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def command_as_json(cmd_type, cmd, hash_key, seed=None):
    config = {
        cmd_type: str(cmd.rstrip()),
    }

    sha256 = hashlib.sha256()
    sha256.update(hash_key.encode())
    if seed is not None:
        sha256.update(seed)
    for key in sorted(config):
        logger.debug("Key: %s, value: %s", key, config[key])
        sha256.update(key.encode())
        sha256.update(("%s" % (config[key])).encode())
    sha256.update(hash_key.encode())
    config["checksum"] = sha256.hexdigest()

    return json.dumps(config)


def calc_hash(key, seed, *args):
    sha256 = hashlib.sha256()
    sha256.update(key.encode())
    if seed is not None:
        sha256.update(seed.encode())
    for value in args:
        logger.debug("Value: %s", value)
        sha256.update(("%s" % (value,)).encode())
    sha256.update(key.encode())

    return sha256.hexdigest()

