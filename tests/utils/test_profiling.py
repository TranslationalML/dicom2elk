# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Tests for dicom2elk.utils.profiling module."""

import os
import pandas as pd

from dicom2elk.utils.profiling import append_profiler_results


def test_append_profiler_results(io_path):
    # Append profiler results to file
    tsv_file = os.path.join(io_path, "test.profile.tsv")
    append_profiler_results(
        tsv_file=tsv_file,
        n_threads=1,
        batch_size=2,
        process_handler="multiprocessing",
        max_memory_usage=1000,
        total_dcm_processed=10,
        total_dcm_skipped=0,
        total_time=10,
    )

    # Check if the file exists
    assert os.path.exists(tsv_file)

    # Read the results
    results = pd.read_csv(tsv_file, sep="\t")

    # Check if the results are correct
    assert results.shape == (1, 8)
    assert results["n_threads"].values[0] == 1
    assert results["batch_size"].values[0] == 2
    assert results["process_handler"].values[0] == "multiprocessing"
    assert results["max_memory_usage"].values[0] == 1000
    assert results["total_dcm_processed"].values[0] == 10
    assert results["total_dcm_skipped"].values[0] == 0
    assert results["total_time"].values[0] == 10

    # Remove the file when done
    os.remove(tsv_file)
