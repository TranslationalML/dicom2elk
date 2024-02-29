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

"""Module for defining profiling related functions."""

import os
import time


def append_profiler_results(
    tsv_file: str,
    n_threads: int,
    batch_size: int,
    process_handler: str,
    max_memory_usage: float,
    total_dcm_processed: int,
    total_dcm_skipped: int,
    total_time: float,
    # total_time_extraction: float,
    # total_time_save: float,
):
    """Append profiler results to profile file.

    Args:
        tsv_file (str): Path to output TSV file that will contain profiler results.
        n_threads (int): Number of threads used for parallel processing.
        batch_size (int): Batch size for extracting and saving/uploading
                          metadata tags from dicom files.
        process_handler (str): Process handler used for parallel/asynchronous processing.
                               Can be either 'multiprocessing' or 'asyncio'.
        max_memory_usage (float): Maximum memory usage.
        total_dcm_processed (int): Total number of dicom files processed.
        total_dcm_skipped (int): Total number of dicom files skipped.
        total_time (float): Total elapsed time in seconds.
        # total_time_extraction (float): Total time spent for extracting tags
        #                                from dicom files (seconds).
        # total_time_save (float): Total time spent for saving/uploading tags
        #                          to JSON/Elasticsearch (seconds).
    """
    if os.path.exists(tsv_file):
        mode = "a"
    else:
        mode = "w"

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

    with open(tsv_file, mode) as f:
        if mode == "w":  # write header at creation
            f.write(
                "\t".join(
                    [
                        "timestamp",
                        "n_threads",
                        "batch_size",
                        "process_handler",
                        "max_memory_usage",
                        "total_dcm_processed",
                        "total_dcm_skipped",
                        "total_time",
                        # "total_time_extraction",
                        # "total_time_save",
                    ]
                )
                + "\n"
            )
        f.write(
            "\t".join(
                [
                    timestamp,
                    str(n_threads),
                    str(batch_size),
                    process_handler,
                    str(max_memory_usage),
                    str(total_dcm_processed),
                    str(total_dcm_skipped),
                    str(total_time),
                    # str(total_time_extraction),
                    # str(total_time_save),
                ]
            )
            + "\n"
        )

