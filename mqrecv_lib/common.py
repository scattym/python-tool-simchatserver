import logging
import os

MQ_HOST = os.environ.get("MQ_HOST", "127.0.0.1")
MQ_USER = os.environ.get("MQ_USER", "guest")
MQ_PASS = os.environ.get("MQ_PASS", "guest")

logger = logging.getLogger(__name__)