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

"""Tests for dicom2elk.core.process module."""

from argparse import Namespace
import os
import sys

from dicom2elk.core.process import process_batches
from dicom2elk.utils.logging import create_logger


def test_process_batches(test_dcm_files, io_path):
    args = Namespace(
        **{
            "n_threads": 2,
            "process_handler": "asyncio",
            "batch_size": 2,
            "sleep_time_ms": 0,
            "output_dir": str(io_path),
            "mode": "json",
        }
    )
    print(args, file=sys.stderr)

    kwargs = {
        "stop_before_pixels": True,
    }

    test_dcm_files_batches = [
        test_dcm_files[i : i + args.batch_size]
        for i in range(0, len(test_dcm_files), args.batch_size)
    ]

    # Test if process_batches returns a list of dictionaries
    # if the number of threads is set to 2 and the method is set to asyncio
    nb_dcm_processed, nb_dcm_skipped = process_batches(
        test_dcm_files_batches, args=args, kwargs=kwargs,
    )

    assert isinstance(nb_dcm_processed, int)
    assert isinstance(nb_dcm_skipped, int)
    assert nb_dcm_processed == len(test_dcm_files)
