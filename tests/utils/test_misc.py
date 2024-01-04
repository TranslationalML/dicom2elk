# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Tests for dicom2elk.utils.misc module."""

from dicom2elk.utils.misc import prepare_file_list_batches


def test_prepare_file_list_batches(test_dcm_files):
   # Prepare batches of dicom files to process
    dcm_list_batches = prepare_file_list_batches(test_dcm_files, 2)

    # Test if the batches are created correctly
    assert len(dcm_list_batches) == len(test_dcm_files) // 2
    assert dcm_list_batches[0] == test_dcm_files[:2]
    assert dcm_list_batches[1] == test_dcm_files[2:4]
    assert dcm_list_batches[2] == test_dcm_files[4:6]
    assert dcm_list_batches[3] == test_dcm_files[6:8]
