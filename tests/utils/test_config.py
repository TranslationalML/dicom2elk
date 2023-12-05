# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Tests for dicom2elk.utils.config module."""

import json
import os

from dicom2elk.utils.config import get_config, set_n_threads


def test_get_config(tmpdir):
    # Create a temporary directory for testing
    output_dir = str(tmpdir.mkdir("output"))

    # Create a sample configuration file
    config_file = os.path.join(output_dir, "sample_config.json")
    with open(config_file, "w") as f:
        f.write(
            json.dumps(
                {
                    "elasticsearch": {
                        "host": "localhost",
                        "port": 9200,
                        "username": "elastic",
                        "password": "changeme",
                    },
                }
            )
        )

    # Test if get_config returns a dictionary
    assert isinstance(get_config(config_file), dict)

    # Test if get_config returns the correct dictionary
    assert get_config(config_file) == {
        "elasticsearch": {
            "host": "localhost",
            "port": 9200,
            "username": "elastic",
            "password": "changeme",
        },
    }


def test_set_n_threads():
    # Test if set_n_threads returns an integer
    assert isinstance(set_n_threads(1), int)

    # Test if set_n_threads returns the correct integer
    assert set_n_threads(1) == 1
    assert set_n_threads(-1) == 1
    assert set_n_threads(0) == 1
    assert set_n_threads(2) == 2
    assert set_n_threads(100) == os.cpu_count()
