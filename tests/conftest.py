# Copyright (C) 2023, The TranslationalML team and Contributors, All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

import os
import shutil
import sqlite3 as sq

import pytest

from pydicom.data import get_testdata_files


@pytest.fixture(scope="session")
def test_dcm_files():
    # Get a list of test DICOM files from pydicom
    test_files = get_testdata_files(pattern="*MR_small*")
    return test_files


@pytest.fixture(scope="session")
def test_gz_file():
    # Get a test GZ file from pydicom
    test_file = get_testdata_files(pattern="*zipMR.gz")[0]
    return test_file


@pytest.fixture(scope="session")
def io_path():
    # Set the path to the input/output directory for test that lies
    # in the same directory as this file
    io_path = os.path.join(os.path.dirname(__file__), "io")
    # Clean the input/output directory if it already exists
    if os.path.exists(io_path):
        shutil.rmtree(io_path)
    os.makedirs(io_path, exist_ok=True)
    return io_path


@pytest.fixture(scope="session")
def test_dcm_files_mega():
    nb_files = 120000
    # Make a list of 120000 times the same test DICOM file from pydicom
    test_files = [
        get_testdata_files(pattern="*MR_small.dcm")[0],
    ] * nb_files
    return test_files


@pytest.fixture(scope="session")
def test_dcm_dir_path(io_path):
    # Get a test DICOM file from pydicom
    test_file = get_testdata_files(pattern="*MR_small.dcm")[0]
    # Clean the directory tp store dicom files if it already exists
    dcm_dir = os.path.join(io_path, "dicom")
    if os.path.exists(dcm_dir):
        shutil.rmtree(dcm_dir)
    os.makedirs(dcm_dir, exist_ok=True)
    # Copy the test DICOM file 9 times
    for i in range(1, 10):
        shutil.copy(test_file, os.path.join(dcm_dir, "test{}.dcm".format(i)))
    return dcm_dir


@pytest.fixture(scope="session")
def db_connection(io_path):
    """Create a temporary database."""
    db_file = os.path.join(str(io_path), "test.db")
    print("Creating temporary database at {}".format(db_file))
    # Ensure the database does not exist
    if os.path.exists(db_file):
        os.remove(db_file)
    # Create a new database
    conn = sq.connect(db_file)
    return conn
