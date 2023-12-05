# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module that defines functions to process DICOM files and metadata."""


from dicom2elk.dicom.metadata import extract_metadata_from_dcm_list, get_dcm_tags_list
from dicom2elk.elasticsearch.api import send_bulk_to_elasticsearch
from dicom2elk.io import write_json_files
from dicom2elk.logging import create_logger


import argparse
import time
import logging


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
                   * the total time spent for extracting tags from dicom files.
                   * the total time spent for saving/uploading tags to JSON/Elasticsearch.
    """
    if kwargs is None:
        kwargs = {}

    total_dcm_processed, total_dcm_skipped = 0, 0
    total_time_extraction = 0
    total_time_save = 0

    for i, dcm_list_batch in enumerate(dcm_list_batches):
        logger.info(
            f"Processing batch #{i+1} of {len(dcm_list_batches)} (batch size: {args.batch_size})"
        )
        # Extract tags from dicom files batch
        tic_extraction = time.perf_counter()
        dcm_tags_list_batch = get_dcm_tags_list(
            dcm_list_batch,
            process_handler=args.process_handler,
            n_threads=args.n_threads,
            sleep_time_ms=args.sleep_time_ms,
            **kwargs,
        )

        # Remove None values
        dcm_tags_list_batch = [
            dcm_tags for dcm_tags in dcm_tags_list_batch if dcm_tags is not None
        ]
        toc_extraction = time.perf_counter()

        # Save JSON files for each dicom file in batch
        tic_save = time.perf_counter()
        if args.dry_run:
            write_json_files(
                json_dicts=dcm_tags_list_batch,
                output_dir=args.output_dir,
                n_threads=args.n_threads,
                sleep_time_ms=args.sleep_time_ms,
            )
        else:
            # Upload JSON representation of dicom files in batch to Elasticsearch
            send_bulk_to_elasticsearch(
                dcm_tags_list=dcm_tags_list_batch, config=args.config
            )
        toc_save = time.perf_counter()

        # Update counters
        total_time_extraction += toc_extraction - tic_extraction
        total_time_save += toc_save - tic_save
        total_dcm_processed += len(dcm_tags_list_batch)
        total_dcm_skipped += len(dcm_list_batch) - len(dcm_tags_list_batch)

    return (
        total_dcm_processed,
        total_dcm_skipped,
        total_time_extraction,
        total_time_save,
    )


def process_batches_optimized(
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
                   * the total time spent for extracting tags from dicom files.
                   * the total time spent for saving/uploading tags to JSON/Elasticsearch.
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
