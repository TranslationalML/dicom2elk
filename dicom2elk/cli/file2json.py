# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Main module."""

import os
import shutil
import sys
import time
import warnings

from dicom2elk.cli.dicom2elk import process
from dicom2elk.info import __packagename__, __version__, __copyright__
from dicom2elk.cli.parser import get_dicom2elk_parser, get_file2json_parser
from dicom2elk.utils.logging import create_logger

def main():
    parser = get_file2json_parser()
    args = parser.parse_args()

    if not args.profile and args.profile_tsv is not None:
        parser.error(
            "The following argument is required when --profile-tsv is specified: --profile"
        )


    # Make sure path are absolute
    args.output_dir = os.path.abspath(args.output_dir)
    args.output_err = os.path.abspath(args.output_err)
    args.output_done = os.path.abspath(args.output_done)
    args.temp_folder = os.path.abspath(args.temp_folder)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    if not os.path.exists(args.output_err):
        os.makedirs(args.output_err)
    if not os.path.exists(args.output_done):
        os.makedirs(args.output_done)
    if not os.path.exists(args.temp_folder):
        os.makedirs(args.temp_folder)

    if args.config is not None:
        args.config = os.path.abspath(args.config)
    if args.profile_tsv is not None:
        args.profile_tsv = os.path.abspath(args.profile_tsv)

    # Create logger
    log_basename = os.path.join(args.output_dir,"file2json.log")
    logger = create_logger(args.log_level, args.output_dir, log_basename)
    warnings.filterwarnings("ignore")

    # Display run summary
    logger.info(
        f"Running file2json version {__version__} with the following arguments:"
    )
    for arg in vars(args):
        logger.info(f"{arg}: {getattr(args, arg)}")

    for root, _, files in os.walk(args.path):
        for file in files:
            # get absolute path of file
            tic = time.perf_counter()
            file_orig = os.path.join(root, file)
            file_dest = os.path.join(args.temp_folder, file)
            file_done = os.path.join(args.output_done, file)
            shutil.move(file_orig, file_dest)

            args.input_dcm_list = file_dest
            process(args)
            shutil.move(file_dest,file_done)
            toc = time.perf_counter()
            # Compute total elapsed time
            total_time = toc - tic

            logger.info(f"Run summary:")
            logger.info(f"Total time: {total_time:.2f} sec.")


    logger.info("Finished!")

    return 0


if __name__ == "__main__":
    sys.exit(main())

