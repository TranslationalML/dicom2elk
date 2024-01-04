# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

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
