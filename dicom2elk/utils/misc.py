# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module for miscellaneous functions."""


def prepare_file_list_batches(file_list: list, batch_size: int):
    """Prepare batches of dicom files to process.

    Args:
        file_list (list): List of files to process.
        batch_size (int): Batch size.

    Returns:
        list: List of batches of files to process.
    """
    file_list_batches = []
    if batch_size > len(file_list):
        batch_size = len(file_list)
    for i in range(0, len(file_list), batch_size):
        file_list_batches.append(file_list[i : i + batch_size])
    return file_list_batches
