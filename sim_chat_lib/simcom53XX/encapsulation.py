import hashlib
import json
import logging

logger = logging.getLogger(__name__)

def command_as_json(cmd, key, seed=None):
    config = {
        "command": str(cmd.rstrip()),
    }

    sha256 = hashlib.sha256()
    sha256.update(key)
    if seed is not None:
        sha256.update(seed)
    for key in sorted(config):
        logger.debug("Key: %s, value: %s", key, config[key])
        sha256.update(key)
        sha256.update("%s" % (config[key]))
    sha256.update("Please press enter:")
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

