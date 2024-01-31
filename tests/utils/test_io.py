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

"""Tests for dicom2elk.utils.io module."""

import json
import os

from dicom2elk.utils.io import read_dcm_list_file, write_json_file, write_json_files


def test_write_json_files(tmpdir):
    # Create a temporary directory for testing
    output_dir = str(tmpdir.mkdir("output"))

    # Create a sample list of JSON dictionaries
    json_dicts = [
        {"name": "John Doe", "age": 30, "filepath": "sample1.dcm"},
        {"name": "Jane Smith", "age": 25, "filepath": "sample2.dcm"},
    ]

    # Write the JSON files
    json_files = write_json_files(json_dicts, output_dir)

    # Test if the JSON files exist
    assert len(json_files) == 2
    for json_file in json_files:
        assert os.path.exists(json_file)

    # Test if the content of the JSON files is correct
    with open(json_files[0], "r") as f:
        content = f.read()
        assert json.loads(content) == {
            "name": "John Doe",
            "age": 30,
            "filepath": "sample1.dcm",
        }

    with open(json_files[1], "r") as f:
        content = f.read()
        assert json.loads(content) == {
            "name": "Jane Smith",
            "age": 25,
            "filepath": "sample2.dcm",
        }


def test_write_json_file(tmpdir):
    # Create a temporary directory for testing
    output_dir = str(tmpdir.mkdir("output"))

    # Create a sample JSON dictionary
    json_dict = {"name": "John Doe", "age": 30}

    # Write the JSON file
    json_file = os.path.join(output_dir, "sample.json")
    write_json_file(json_file, json_dict)

    # Test if the JSON file exists
    assert os.path.exists(json_file)

    # Test if the content of the JSON file is correct
    with open(json_file, "r") as f:
        content = f.read()
        assert json.loads(content) == {"name": "John Doe", "age": 30}


def test_read_dcm_list_file(test_dcm_files, tmpdir):
    # Write a list of DICOM files
    dcm_list_file = os.path.join(str(tmpdir.mkdir("output")), "dcm_list.txt")
    with open(dcm_list_file, "w") as f:
        for dcm_file in test_dcm_files:
            f.write(dcm_file + "\n")
    print(dcm_list_file)
    # Test if read_dcm_list_file returns a list
    assert isinstance(read_dcm_list_file(dcm_list_file), list)

    # Test if read_dcm_list_file returns the correct list
    assert read_dcm_list_file(dcm_list_file) == test_dcm_files