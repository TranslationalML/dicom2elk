# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module for miscellaneous functions."""


def prepare_dcm_list_batches(dcm_list: list, batch_size: int):
    """Prepare batches of dicom files to process.

    Args:
        dcm_list (list): List of dicom files to process.
        batch_size (int): Batch size for extracting and saving/uploading
                          metadata tags from dicom files.

    Returns:
        list: List of batches of dicom files to process.
    """
    dcm_list_batches = []
    if batch_size > len(dcm_list):
        batch_size = len(dcm_list)
    for i in range(0, len(dcm_list), batch_size):
        dcm_list_batches.append(dcm_list[i : i + batch_size])
    return dcm_list_batches

