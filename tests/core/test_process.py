# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

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
