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
