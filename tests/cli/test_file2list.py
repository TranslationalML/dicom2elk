# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Tests for file2list CLI."""

import os
import glob
import shutil
import pytest


@pytest.mark.script_launch_mode("subprocess")
def test_file2list(script_runner, test_dcm_dir_path, io_path):
    ouput_dir = os.path.join(str(io_path), "test_file2list")
    if os.path.exists(ouput_dir):
        shutil.rmtree(ouput_dir)
    os.makedirs(ouput_dir, exist_ok=True)
    # Run the script
    ret = script_runner.run(
        "file2list",
        "-p",
        test_dcm_dir_path,
        "-o",
        ouput_dir,
        "--batch-size",
        "2",
        "--db-file",
        os.path.join(str(io_path), "test.db"),
        "--db-table",
        "test_table",
    )
    # Check if the script runs successfully
    assert ret.success

    # Check if the output files exist    
    assert len(glob.glob(os.path.join(ouput_dir, "*.txt"))) == 5
    assert len(glob.glob(os.path.join(ouput_dir, "*.log"))) == 1
    assert os.path.exists(os.path.join(str(io_path), "test.db"))
