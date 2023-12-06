# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module that defines functions to process DICOM files and metadata."""

import argparse
import logging

from dicom2elk.core.dicom.metadata import extract_metadata_from_dcm_list
from dicom2elk.utils.logging import create_logger


def process_batches(
    dcm_list_batches: list,
    args: argparse.Namespace,
    logger: logging.Logger = create_logger("INFO"),
    kwargs: dict = None,
):
    """Process batches of dicom files.

    Args:
        dcm_list_batches (list): List of batches of dicom files to process.
        args (argparse.Namespace): Arguments passed to the main function.
        logger (logging.Logger): Logger instance.
        **kwargs: Arbitrary keyword arguments to pass to the `dcmread` function.

    Returns:
        tuple: Tuple containing:
                   * the number of dicom files processed.
                   * the number of dicom files skipped.
    """
    if kwargs is None:
        kwargs = {}

    total_dcm_processed, total_dcm_skipped = 0, 0
    for i, dcm_list_batch in enumerate(dcm_list_batches):
        logger.info(
            f"Processing batch #{i+1} of {len(dcm_list_batches)} (batch size: {args.batch_size})"
        )
        processed_dcm_list_batch = extract_metadata_from_dcm_list(
            dcm_list_batch,
            output_dir=args.output_dir,
            process_handler=args.process_handler,
            mode=args.mode,
            n_threads=args.n_threads,
            sleep_time_ms=args.sleep_time_ms,
            logger=logger,
            **kwargs,
        )

        # Remove None values
        processed_dcm_list_batch = [
            dcm_file for dcm_file in processed_dcm_list_batch if dcm_file is not None
        ]

        # Update counters
        total_dcm_processed += len(processed_dcm_list_batch)
        total_dcm_skipped += len(dcm_list_batch) - len(processed_dcm_list_batch)

    return total_dcm_processed, total_dcm_skipped
