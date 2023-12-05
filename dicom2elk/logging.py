# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module for logger."""

import os
import logging


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors.

    Note:
        This class was copied from the following StackOverflow post:
        https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output.
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def create_logger(level=logging.INFO, output_dir: str = None):
    """Create and configure logger.

    Args:
        level (int): Logging level.
        output_dir (str): Output directory.

    Returns:
        logging.Logger: Logger.
    """
    _logger = logging.getLogger()
    _logger.setLevel(level)
    _handler = logging.StreamHandler()
    _handler.setFormatter(CustomFormatter())

    # Make sure we won't have duplicated messages in the output
    # See https://stackoverflow.com/questions/641420/how-should-i-log-while-using-multiprocessing-in-python
    if not len(_logger.handlers): 
        _logger.addHandler(_handler)
        if output_dir is not None:
            _log_file = os.path.join(output_dir, "dicom2elk.log")
            _handler = logging.FileHandler(_log_file)
            _handler.setFormatter(CustomFormatter())
            _logger.addHandler(_handler)
    return _logger
