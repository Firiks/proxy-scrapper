"""
Configures logging for the project.
"""

import os
import logging

def get_logger(name):

    # dirs and files
    CURRENT_DIR = os.path.dirname(__file__)
    LOG_DIR = os.path.join(CURRENT_DIR, 'logs')
    LOG_FILE = os.path.join(LOG_DIR, f'{name}.log')

    # create dirs
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # get logger by name
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create a file handler
    file_handler = logging.FileHandler(LOG_FILE, mode='w')
    file_handler.setLevel(logging.INFO)

    # create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # create a formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

    # add the formatter to the handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger