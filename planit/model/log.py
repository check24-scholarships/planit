# -*- coding: utf-8 -*-

"""
Logging

Provides uniform logging.
"""

import logging
import sys
import os
from .. import resources

# Path of the log dir
basePath: str = 'log/'

# TODO: Type hint for returned logger
def createLogger(name):
    """ Create a logger with a file and stream handler on debug level. """

    # Name the log file after the logger
    path: str = os.path.join(resources.get(basePath), f'{name}.log')

    # Create file handler and stream handler for console logging
    fileHandler: logging.FileHandler = logging.FileHandler(path)
    streamHandler: logging.StreamHandler = logging.StreamHandler(sys.stdout)

    # Set logging format
    frm: logging.Formatter = logging.Formatter(
        '{asctime} {levelname}: {message}',
        '%Y-%m-%d %H:%M:%S',
        style = '{'
    )
    fileHandler.setFormatter(frm)
    streamHandler.setFormatter(frm)

    # Create logger and add handlers
    # TODO: Type hint for logger
    logger = logging.getLogger()
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.DEBUG)

    return logger
