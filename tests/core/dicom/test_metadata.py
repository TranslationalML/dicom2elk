# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Tests for dicom2elk.core.dicom.metadata module."""

import os

from dicom2elk.core.dicom.metadata import (
    extract_metadata_from_dcm,
    extract_metadata_from_dcm_list,
)


def test_extract_metadata_from_dcm_list_asyncio(test_dcm_files, io_path):
    # Test if extract_metadata_from_dcm_list returns a list of dictionaries
    # if the number of threads is set to 2 and the method is set to asyncio
    dcm_json_files_list = extract_metadata_from_dcm_list(
        test_dcm_files,
        n_threads=2,
        process_handler="asyncio",
        mode="json",
        output_dir=str(io_path),
    )
    assert isinstance(dcm_json_files_list, list)
    for dcm_json_file in dcm_json_files_list:
        assert os.path.exists(dcm_json_file)
        os.remove(dcm_json_file)


def test_extract_metadata_from_dcm_list_singleproc(test_dcm_files, io_path):
    # Test if extract_metadata_from_dcm_list returns a list of dictionaries
    dcm_json_files_list = extract_metadata_from_dcm_list(
        test_dcm_files, n_threads=1, mode="json", output_dir=str(io_path)
    )
    assert isinstance(dcm_json_files_list, list)
    for dcm_json_file in dcm_json_files_list:
        assert os.path.exists(dcm_json_file)
        os.remove(dcm_json_file)


def test_extract_metadata_from_dcm_list_multiproc(test_dcm_files, io_path):
    # Test if extract_metadata_from_dcm_list returns a list of dictionaries
    dcm_json_files_list = extract_metadata_from_dcm_list(
        test_dcm_files, n_threads=2, mode="json", output_dir=str(io_path)
    )
    assert isinstance(dcm_json_files_list, list)
    for dcm_json_file in dcm_json_files_list:
        assert os.path.exists(dcm_json_file)
        os.remove(dcm_json_file)


def test_extract_metadata_from_dcm_wrong(test_gz_file, io_path):
    # Test if extract_metadata_from_dcm returns None if the file is not a DICOM file
    # Here we use a GZ file instead of a DICOM file
    assert (
        extract_metadata_from_dcm(test_gz_file, mode="json", output_dir=str(io_path))
        == None
    )


def test_extract_metadata_from_dcm(test_dcm_files, io_path):
    for dcm_file in test_dcm_files:
        # Test if extract_metadata_from_dcm creates a JSON file
        assert os.path.exists(
            extract_metadata_from_dcm(dcm_file, mode="json", output_dir=str(io_path))
        )
