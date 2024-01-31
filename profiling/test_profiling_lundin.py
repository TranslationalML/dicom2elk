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

import os
import pytest
import glob
import shutil


@pytest.fixture(scope="session")
def test_real_dcm_files():
    # Get a list of real DICOM files
    dcm_files = glob.glob("/home/stourbie/Data/LUNDIN/DICOMS/*/*/*/*")
    # estimate total size of DICOM files
    total_size = sum([os.path.getsize(dcm_file) for dcm_file in dcm_files])
    return dcm_files


@pytest.fixture(scope="session")
def output_dir():
    output_dir = "/home/stourbie/Code/GitHub/dicom2elk/results"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


# @pytest.mark.parametrize("n_threads", [1, 2, 4, 8, 16, 31])
# @pytest.mark.parametrize("batch_size", [5000, 10000, 20000, 40000, 60000, 80000, 100000, 120000])
# @pytest.mark.parametrize("process_handler", ["multiprocessing", "asyncio"])
# @pytest.mark.script_launch_mode("subprocess")
# def test_dryrun_dicom2elk_profiling(
#     script_runner,
#     tmpdir,
#     test_dcm_files_mega,
#     io_path,
#     n_threads,
#     batch_size,
#     process_handler,
# ):
#     # Create a temporary text file containing a list of DICOM files
#     dcm_list_file = os.path.join(str(tmpdir.mkdir("output")), "dcm_list.txt")
#     with open(dcm_list_file, "w") as f:
#         for dcm_file in test_dcm_files_mega:
#             f.write(dcm_file + "\n")

#     # Create a temporary directory for testing
#     output_dir = str(io_path)

#     # Run the script
#     ret = script_runner.run(
#         "dicom2elk",
#         "-i",
#         dcm_list_file,
#         "-o",
#         output_dir,
#         "--n-threads",
#         str(n_threads),
#         "--batch-size",
#         str(batch_size),
#         "--process-handler",
#         process_handler,
#         "--dry-run",
#         "--profile",
#     )

#     # Test if the script runs successfully
#     assert ret.success

#     # Test if the output profile file exists
#     assert os.path.exists(os.path.join(output_dir, "dcm_list.txt.profile.tsv"))


@pytest.mark.parametrize("n_threads", [31, 16, 8, 4, 2, 1])
@pytest.mark.parametrize("batch_size", [10000, 20000, 40000, 60000])
@pytest.mark.parametrize("process_handler", ["asyncio", "multiprocessing"])
@pytest.mark.script_launch_mode("subprocess")
def test_dryrun_dicom2elk_profiling(
    script_runner,
    test_real_dcm_files,
    output_dir,
    n_threads,
    batch_size,
    process_handler,
):
    # Create a temporary text file containing a list of DICOM files
    dcm_list_file = os.path.join(output_dir, "dcm_list_profiling_lundin.txt")
    with open(dcm_list_file, "w") as f:
        for dcm_file in test_real_dcm_files:
            f.write(dcm_file + "\n")

    # Create a temporary directory for testing
    output_dir = str(output_dir)

    # Run the script
    ret = script_runner.run(
        "dicom2elk",
        "-i",
        dcm_list_file,
        "-o",
        output_dir,
        "--n-threads",
        str(n_threads),
        "--batch-size",
        str(batch_size),
        "--process-handler",
        process_handler,
        "--mode",
        "json",
        "--profile",
        "--profile-tsv",
        os.path.join(output_dir, "lundin_dcm_list.txt.profile.tsv")
    )

    # Test if the script runs successfully
    assert ret.success
