# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Tests for dicom2elk.utils.logging module."""

import os

from dicom2elk.utils.logging import create_logger


def test_create_logger(tmpdir):
    # Create a temporary directory for testing
    output_dir = str(tmpdir.mkdir("output"))

    # Create a logger
    logger = create_logger("INFO", output_dir)

    # Test if the logger is created
    assert logger is not None

    # Test if the log file exists
    assert os.path.exists(os.path.join(output_dir, "dicom2elk.log"))