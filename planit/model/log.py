# -*- coding: utf-8 -*-

'''
Logging

Provides uniform logging.
'''

import logging
import sys

# Path to the log dir
basePath: str = '../../log/'

# TODO: Type hint for returned logger
def createLogger(name):

    '''
    Create a logger with a file and stream handler on debug level.
    '''

    # Name the log file after the logger
    path: str = '{}{}.log'.format(basePath, name)

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
