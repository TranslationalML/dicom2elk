# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Main module."""

import os
import sys
import time
import memory_profiler
import warnings

from dicom2elk.info import __packagename__, __version__, __copyright__
from dicom2elk.cli.parser import get_dicom2elk_parser
from dicom2elk.core.process import process_batches
from dicom2elk.utils.io import read_dcm_list_file
from dicom2elk.utils.logging import create_logger
from dicom2elk.utils.config import set_n_threads
from dicom2elk.utils.profiling import append_profiler_results
from dicom2elk.utils.misc import prepare_dcm_list_batches


def main():
    parser = get_dicom2elk_parser()
    args = parser.parse_args()

    if not args.profile and args.profile_tsv is not None:
        parser.error(
            "The following argument is required when --profile-tsv is specified: --profile"
        )

    # Create logger
    logger = create_logger(args.log_level, args.output_dir)
    warnings.filterwarnings("ignore")

    # Make sure path are absolute
    args.input_dcm_list = os.path.abspath(args.input_dcm_list)
    args.output_dir = os.path.abspath(args.output_dir)
    if args.config is not None:
        args.config = os.path.abspath(args.config)
    if args.profile_tsv is not None:
        args.profile_tsv = os.path.abspath(args.profile_tsv)

    # Handle n_threads argument
    # If n_threads is invalid, it is set to default value
    # (1 if n_threads < 1, cpu_count() if n_threads > cpu_count()
    args.n_threads = set_n_threads(args.n_threads)

    # Handle output profile tsv file path if profile is specified
    # but not profile_tsv
    if args.profile and args.profile_tsv is None:
        args.profile_tsv = os.path.join(
            args.output_dir, os.path.basename(args.input_dcm_list) + ".profile.tsv"
        )

    # Create output directory if it does not exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Display run summary
    logger.info(
        f"Running dicom2elk version {__version__} with the following arguments:"
    )
    for arg in vars(args):
        logger.info(f"{arg}: {getattr(args, arg)}")

    # Load dicom list file
    dcm_list = read_dcm_list_file(args.input_dcm_list)

    # Define  arguments to pass to the `dcmread` function
    # in `get_dcm_tags_list`
    kwargs = {
        "stop_before_pixels": True,
    }

    # Prepare batches of dicom files to process
    dcm_list_batches = prepare_dcm_list_batches(dcm_list, args.batch_size)

    if args.profile:
        # Process batches of dicom files with memory profiler
        profiler_options = {
            "interval": 0.5,
            "multiprocess": True,
            "retval": True,
            "max_usage": True,
            "backend": "psutil",
        }
        logger.info(f"Profiler options: {profiler_options}")

        tic = time.perf_counter()
        # (memory_usage, retval) = memory_profiler.memory_usage(
        #     (process_batches, (dcm_list_batches, args, kwargs)),
        #     **profiler_options,
        # )
        (memory_usage, retval) = memory_profiler.memory_usage(
            (process_batches, (dcm_list_batches, args, logger, kwargs)),
            **profiler_options,
        )
        toc = time.perf_counter()

        # Unpack total_dcm_processed and total_dcm_skipped from retval
        (
            total_dcm_processed,
            total_dcm_skipped,
            # total_time_extraction,
            # total_time_save,
        ) = retval

        # Compute total elapsed time
        total_time = toc - tic

        append_profiler_results(
            args.profile_tsv,
            args.n_threads,
            args.batch_size,
            args.process_handler,
            memory_usage,
            total_dcm_processed,
            total_dcm_skipped,
            total_time,
            # total_time_extraction,
            # total_time_save,
        )
    else:
        # Process batches of dicom files
        tic = time.perf_counter()
        (
            total_dcm_processed,
            total_dcm_skipped,
            # total_time_extraction,
            # total_time_save,
        ) = process_batches(dcm_list_batches, args, logger, kwargs)
        toc = time.perf_counter()
        # Compute total elapsed time
        total_time = toc - tic

    logger.info(f"Run summary:")
    logger.info(f"Number of dicom files processed: {total_dcm_processed}")
    logger.info(f"Number of dicom files skipped: {total_dcm_skipped}")
    # logger.info(
    #     f"Total time: {total_time:.2f} sec. (Extraction: {total_time_extraction:.2f} sec., Save: {total_time_save:.2f} sec.)"
    # )
    logger.info(f"Total time: {total_time:.2f} sec.")
    logger.info("Finished!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
