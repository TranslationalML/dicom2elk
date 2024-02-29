# Copyright 2023-2024 Lausanne University and Lausanne University Hospital, Switzerland & Contributors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


def create_logger(
    level=logging.INFO, output_dir: str = None, log_basename: str = "dicom2elk.log"
):
    """Create and configure logger.

    Args:
        level (int): Logging level.
        output_dir (str): Output directory.
        log_basename (str): Basename of the log file.

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
        _log_file = os.path.join(output_dir, log_basename)
        _handler = logging.FileHandler(_log_file)
        _handler.setFormatter(CustomFormatter())
        _logger.addHandler(_handler)
    return _logger


def get_logger_basefilename(logger):
    """Finds the logger base filename.

    Args:
        logger(logging.Logger): Logger.

    Return:
        log_file(str): Path to log file.
    """
    log_file = None
    if logger is not None:
        log_file = logger.handlers[1].baseFilename
    return log_file
