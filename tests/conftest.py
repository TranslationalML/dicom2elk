# Copyright (C) 2023, The TranslationalML team and Contributors, All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

import os
import pytest
from pydicom.data import get_testdata_files


@pytest.fixture(scope="module")
def test_dcm_files():
    # Get a list of test DICOM files from pydicom
    test_files = get_testdata_files(pattern="*MR_small*")
    return test_files


@pytest.fixture(scope="module")
def test_gz_file():
    # Get a test GZ file from pydicom
    test_file = get_testdata_files(pattern="*zipMR.gz")[0]
    return test_file


@pytest.fixture(scope="module")
def io_path():
    # Set the path to the input/output directory for test that lies
    # in the same directory as this file
    io_path = os.path.join(os.path.dirname(__file__), "io")
    if not os.path.exists(io_path):
        os.makedirs(io_path, exist_ok=True)
    return io_path
