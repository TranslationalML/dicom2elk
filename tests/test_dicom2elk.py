# Copyright (C) 2023, The TranslationalML team and Contributors, All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

import json
import os

import pytest

from dicom2elk.dicom2elk import (
    get_parser,
    create_logger,
    get_config,
    set_n_threads,
    get_dcm_list,
    get_dcm_tags,
    get_dcm_tags_list,
    write_json_file,
    write_json_files,
)


def test_get_parser():
    # Test if get_parser returns a parser
    assert get_parser() is not None


def test_set_n_threads():
    # Test if set_n_threads returns an integer
    assert isinstance(set_n_threads(1), int)

    # Test if set_n_threads returns the correct integer
    assert set_n_threads(1) == 1
    assert set_n_threads(-1) == 1
    assert set_n_threads(0) == 1
    assert set_n_threads(2) == 2
    assert set_n_threads(100) == os.cpu_count()


def test_create_logger(tmpdir):
    # Create a temporary directory for testing
    output_dir = str(tmpdir.mkdir("output"))

    # Create a logger
    logger = create_logger("INFO", output_dir)

    # Test if the logger is created
    assert logger is not None

    # Test if the log file exists
    assert os.path.exists(os.path.join(output_dir, "dicom2elk.log"))


def test_get_config(tmpdir):
    # Create a temporary directory for testing
    output_dir = str(tmpdir.mkdir("output"))

    # Create a sample configuration file
    config_file = os.path.join(output_dir, "sample_config.json")
    with open(config_file, "w") as f:
        f.write(
            json.dumps(
                {
                    "elasticsearch": {
                        "host": "localhost",
                        "port": 9200,
                        "username": "elastic",
                        "password": "changeme",
                    },
                }
            )
        )

    # Test if get_config returns a dictionary
    assert isinstance(get_config(config_file), dict)

    # Test if get_config returns the correct dictionary
    assert get_config(config_file) == {
        "elasticsearch": {
            "host": "localhost",
            "port": 9200,
            "username": "elastic",
            "password": "changeme",
        },
    }


def test_get_dcm_list(test_dcm_files, tmpdir):
    # Write a list of DICOM files
    dcm_list_file = os.path.join(str(tmpdir.mkdir("output")), "dcm_list.txt")
    with open(dcm_list_file, "w") as f:
        for dcm_file in test_dcm_files:
            f.write(dcm_file + "\n")
    print(dcm_list_file)
    # Test if get_dcm_list returns a list
    assert isinstance(get_dcm_list(dcm_list_file), list)

    # Test if get_dcm_list returns the correct list
    assert get_dcm_list(dcm_list_file) == test_dcm_files


def test_get_dcm_tags(test_dcm_files):
    for dcm_file in test_dcm_files:
        # Test if get_dcm_tags returns a dictionary
        assert isinstance(get_dcm_tags(dcm_file), dict)


def test_get_dcm_tags_wrong(test_gz_file):
    # Test if get_dcm_tags returns None if the file is not a DICOM file
    # Here we use a GZ file instead of a DICOM file
    assert get_dcm_tags(test_gz_file) == None


def test_get_dcm_tags_list_multiproc(test_dcm_files):
    # Test if get_dcm_tags_list returns a list of dictionaries
    dcm_tags_list = get_dcm_tags_list(test_dcm_files, n_threads=2)
    assert isinstance(dcm_tags_list, list)
    for dcm_tags in dcm_tags_list:
        assert isinstance(dcm_tags, dict)


def test_get_dcm_tags_list_singleproc(test_dcm_files):
    # Test if get_dcm_tags_list returns a list of dictionaries
    dcm_tags_list = get_dcm_tags_list(test_dcm_files, n_threads=1)
    assert isinstance(dcm_tags_list, list)
    for dcm_tags in dcm_tags_list:
        assert isinstance(dcm_tags, dict)


def test_get_dcm_tags_list_asyncio(test_dcm_files):
    # Test if get_dcm_tags_list returns a list of dictionaries
    # if the number of threads is set to 2 and the method is set to asyncio
    dcm_tags_list = get_dcm_tags_list(
        test_dcm_files, n_threads=2, parallel_mode="asyncio"
    )
    assert isinstance(dcm_tags_list, list)
    for dcm_tags in dcm_tags_list:
        assert isinstance(dcm_tags, dict)


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
        "--dry-run",
    )

    # Test if the script runs successfully
    assert ret.success

    # Test if the output files exist
    assert os.path.exists(os.path.join(output_dir, "dicom2elk.log"))
    output_files = [os.path.basename(f) + ".json" for f in test_dcm_files]
    for output_file in output_files:
        assert os.path.exists(os.path.join(output_dir, output_file))


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
            "dicom2elk", "-i", dcm_list_file, "--n-threads", "2", "--dry-run"
        ).returncode
        == 2
    )

