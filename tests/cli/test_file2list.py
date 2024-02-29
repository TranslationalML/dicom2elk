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
