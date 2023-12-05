# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module that provides functions to read the configuration file storing the Elasticsearch server information."""


import json
import logging

from dicom2elk.utils.logging import create_logger
from os import cpu_count


def get_config(config_file: str):
    """Load config file in JSON format.

    Args:
        config_file (str): Path to config file in JSON format.

    Returns:
        dict: Dictionary containing all variables related to Elasticsearch instance.
    """
    with open(config_file, "r") as f:
        config = json.load(f)
    return config


def set_n_threads(n_threads: int, logger: logging.Logger = create_logger("INFO")):
    """Set number of threads to use for parallel processing.

    Args:
        n_threads (int): Number of threads to use for parallel processing.
        logger (logging.Logger): Logger instance.
    """
    if n_threads < 1:
        logger.warning(f"Number of threads ({n_threads}) must be greater than 0")
        logger.warning("Setting number of threads to 1")
        n_threads = 1
    elif n_threads > cpu_count():
        logger.warning(
            f"Number of threads ({n_threads}) is greater than the number of CPUs ({cpu_count()})"
        )
        logger.warning("Setting number of threads to the number of CPUs")
        n_threads = cpu_count()
    return n_threads
