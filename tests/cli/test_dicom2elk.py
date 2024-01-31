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

"""Tests for dicom2elk CLI."""

import os
import pytest


@pytest.mark.script_launch_mode("subprocess")
def test_dryrun_dicom2elk(script_runner, tmpdir, test_dcm_files, io_path):
    # Create a temporary text file containing a list of DICOM files
    dcm_list_file = os.path.join(str(tmpdir.mkdir("output")), "dcm_list.txt")
    with open(dcm_list_file, "w") as f:
        for dcm_file in test_dcm_files:
            f.write(dcm_file + "\n")

    # Create a temporary directory for testing
    output_dir = str(io_path)

    # Run the script
    ret = script_runner.run(
        "dicom2elk",
        "-i",
        dcm_list_file,
        "-o",
        output_dir,
        "--n-threads",
        "2",
        "--mode",
        "json",
        "--profile",
    )

    # Test if the script runs successfully
    assert ret.success

    # Test if the output files exist
    log_basename = ".".join(
        [os.path.splitext(os.path.basename(dcm_list_file))[0], "log"]
    )
    assert os.path.exists(os.path.join(output_dir, log_basename))
    # It generates only one JSON file as SOP Instance UID is the same
    # for all DICOM files in the test set
    assert os.path.exists(
        os.path.join(output_dir, "1.3.6.1.4.1.5962.1.1.4.1.1.20040826185059.5457.json")
    )


@pytest.mark.script_launch_mode("subprocess")
def test_dryrun_dicom2elk_no_output_dir(script_runner, tmpdir, test_dcm_files):
    # Create a temporary text file containing a list of DICOM files
    dcm_list_file = os.path.join(str(tmpdir.mkdir("output")), "dcm_list.txt")
    with open(dcm_list_file, "w") as f:
        for dcm_file in test_dcm_files:
            f.write(dcm_file + "\n")

    # Run the script
    assert (
        script_runner.run(
            "dicom2elk", "-i", dcm_list_file, "--n-threads", "2", "--mode", "json"
        ).returncode
        == 2
    )
