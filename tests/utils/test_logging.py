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