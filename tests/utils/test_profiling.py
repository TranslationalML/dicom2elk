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
