#!/usr/bin/env python
import logging

logger = logging.getLogger(__name__)
"""
payload $$<Data identifier><Data length>,<IMEI>,<Command type>,<Command><*Checksum>\r\n
"""
