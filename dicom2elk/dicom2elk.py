# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Main module."""

import os
import argparse
import logging
import json
import sys
import time
import memory_profiler

from os import cpu_count
from concurrent.futures import ThreadPoolExecutor
import asyncio
import tqdm
from tqdm.asyncio import tqdm_asyncio
import nest_asyncio

import warnings

from pydicom import dcmread

from elasticsearch import Elasticsearch
from elasticsearch import helpers


from dicom2elk.info import __packagename__, __version__, __copyright__

# This has to be imported before importing multiprocessing Pool
# See https://stackoverflow.com/questions/57354700/starmap-combined-with-tqdm
from dicom2elk.istarmap import istarmap  # noqa: E402
from multiprocessing import Pool


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors.

    Note:
        This class was copied from the following StackOverflow post:
        https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output.
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def create_logger(level=logging.INFO, output_dir: str = None):
    """Create and configure logger.

    Args:
        level (int): Logging level.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)
    if output_dir is not None:
        log_file = os.path.join(output_dir, "dicom2elk.log")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(CustomFormatter())
        logger.addHandler(handler)
    return logger


def get_parser():
    parser = argparse.ArgumentParser(
        "dicom2elk: A simple and fast package that extracts relevant tags from dicom files "
        "and uploads them in JSON format to elasticsearch.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input-dcm-list",
        type=str,
        required=True,
        help="Text file providing a list of dicom files to process",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Config file in JSON format which defines all variables related to "
        "Elasticsearch instance (url, port, index, user, pwd)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        required=True,
        help="Specify an output directory to save the log file. "
        "If --dry-run is specified, all JSON files are also saved in this directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="When specified, extracted tags for each dicom file of the list are "
        "saved in distinct JSON files in the output directory",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
    )
    parser.add_argument(
        "-n",
        "--n-threads",
        type=int,
        default=1,
        help="Number of threads to use for parallel processing",
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=10000,
        help="Batch size for extracting and saving/uploading "
        "metadata tags from dicom files",
    )
    parser.add_argument(
        "-p",
        "--process-handler",
        type=str,
        default="multiprocessing",
        choices=["multiprocessing", "asyncio"],
        help="Process handler to use for parallel/asynchronous processing. "
        "Can be either 'multiprocessing' or 'asyncio'",
    )
    parser.add_argument(
        "-s",
        "--sleep-time-ms",
        type=float,
        default=0,
        help="Sleep time in milliseconds to wait between each file processing. "
        "This might be useful to avoid overloading the system.",
    )
    parser.add_argument(  # boolean option to perform or not memory profiling
        "--profile",
        action="store_true",
        help="When specified, performance / memory profiling is performed and results are saved. "
        "If --profile-tsv is specified, results are saved in the specified TSV file. "
        "Otherwise, results are saved in a TSV file named after the input dicom list file "
        "with the suffix '.profile.tsv' in the specified `output_dir` directory.",
    )
    parser.add_argument(
        "--profile-tsv",
        type=str,
        default=None,

        help="Specify a TSV file to save mem/perf profiling results.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{__packagename__} {__version__}\n\n{__copyright__}",
    )
    return parser


def get_config(config_file: str):
    """Load config file in JSON format.

    Args:
        config_file (str): Path to config file in JSON format.

    Returns:
        dict: Dictionary containing all variables related to Elasticsearch instance.
    """
    with open(config_file, "r") as f:
        config = json.load(f)
    return config


def get_dcm_list(dcm_list_file):
    """Load dicom list file.

    Args:
        dcm_list_file (str): Path to dicom list file.

    Returns:
        list: List of dicom files to process.
    """
    with open(dcm_list_file, "r") as f:
        dcm_list = f.read().splitlines()
    return dcm_list


def get_dcm_tags(dcm_file: str, sleep_time_ms: str = 0, kwargs: dict = None):
    """Extract relevant tags from dicom file.

    Args:
        dcm_file (str): Path to dicom file.
        sleep_time_ms (float): Sleep time in milliseconds to wait before processing
                               dicom file.
        kwargs: Arbitrary keyword arguments to pass to the `dcmread` function.
                In particular, the `stop_before_pixels` argument can be used
                to stop reading file before reading in pixel data when set to True.

    Returns:
        json_dict: Dictionary representation of the Dataset conforming
                   to the DICOM JSON Model as described in the
                   DICOM Standard, Part 18
    """
    if kwargs is None:
        kwargs = {}
    logger = create_logger()
    logger.debug(f"Processing {dcm_file}")
    stop_before_pixels = kwargs.pop("stop_before_pixels", True)
    try:
        dcm_dataset = dcmread(dcm_file, stop_before_pixels=stop_before_pixels)
        json_dict = dcm_dataset.to_json_dict()
        json_dict["filepath"] = dcm_file
    except Exception as e:
        logging.error(f"Error while processing {dcm_file}: {e}")
        time.sleep(sleep_time_ms)
        return None
    time.sleep(sleep_time_ms)
    return json_dict


def get_dcm_tags_list(
    dcm_list: list,
    process_handler: str = "multiprocessing",
    n_threads: int = 1,
    sleep_time_ms: float = 0,
    **kwargs,
):
    """Extract list of dictionary representation of the DICOM files conforming to the DICOM JSON Model.

    It uses the `to_json_dict` method of the pydicom package.

    It can be parallelized using the `n_threads` argument which leverages the asyncio package.

    Args:
        dcm_list (list): List of dicom files to process.
        process_handler (str): Process handler to use for parallel/asynchronous processing.
                               Can be either 'multiprocessing' or 'asyncio'.
        n_threads (int): Number of threads to use for parallel/asynchronous processing.
                         Defaults to 1.
        sleep_time_ms (float): Sleep time in milliseconds to wait between each file processing.
                               Defaults to 0.
        **kwargs: Arbitrary keyword arguments to pass to the `dcmread` function.

    Returns:
        list: List of dictionary representation of the DICOM files conforming to the
              `DICOM JSON Model <http://dicom.nema.org/medical/dicom/current/output/chtml/part18/chapter_F.html>`_.

    References:
        https://pydicom.github.io/pydicom/dev/reference/generated/pydicom.dataset.Dataset.html#pydicom.dataset.Dataset.to_json_dict
    """
    if n_threads > 1 and process_handler == "asyncio":
        nest_asyncio.apply()
        # Run asyncio tasks in a limited thread pool.
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor, get_dcm_tags, dcm_file, sleep_time_ms, kwargs
                )
                for dcm_file in dcm_list
            ]
            try:
                dcm_tags_list = loop.run_until_complete(tqdm_asyncio.gather(*tasks))
            finally:
                loop.close()
    elif n_threads > 1 and process_handler == "multiprocessing":
        with Pool(n_threads) as p:
            # prepare arguments
            args = zip(
                dcm_list, [sleep_time_ms] * len(dcm_list), [kwargs] * len(dcm_list)
            )
            dcm_tags_list = tqdm.tqdm(
                p.istarmap(
                    get_dcm_tags,
                    args,
                ),
                total=len(dcm_list),
                desc="Extracting tags",
                unit="file",
            )
            dcm_tags_list = list(dcm_tags_list)
    else:
        dcm_tags_list = [
            get_dcm_tags(dcm_file, sleep_time_ms, kwargs) for dcm_file in dcm_list
        ]
    return dcm_tags_list


def write_json_file(json_file: str, json_dict: dict, sleep_time_ms: float = 0):
    """Write JSON file.

    Args:
        json_file (str): Path to JSON file.
        json_dict (dict): Dictionary to save in JSON file.
        sleep_time_ms (float): Sleep time in milliseconds to wait after writing
                               JSON file.
    """
    logger = create_logger()

    with open(json_file, "w") as f:
        json.dump(json_dict, f, indent=4)

    if not os.path.exists(json_file):
        logger.warning(f"JSON file {json_file} not found")
        time.sleep(sleep_time_ms)
        return None

    time.sleep(sleep_time_ms)
    return json_file


def write_json_files(
    json_dicts: list,
    output_dir: str,
    n_threads: int = 1,
    sleep_time_ms: float = 0,
    logger: logging.Logger = None,
):
    """Write JSON files.

    Args:
        json_dicts (list): List of dictionaries to save in JSON files
                           produced by `get_dcm_tags_list`.
        output_dir (str): Path to output directory.
        n_threads (int): Number of threads to use for parallel processing.
        logger (logging.Logger): Logger object.

    Note:
        The JSON files are named after the dicom files from which the
        tags were extracted.

    Returns:
        list: List of paths to JSON files.
    """
    if logger is None:
        logger = create_logger()

    json_files = []

    if n_threads > 1:
        args = zip(
            [
                os.path.join(
                    output_dir, os.path.basename(json_dict["filepath"]) + ".json"
                )
                for json_dict in json_dicts
            ],
            json_dicts,
            [sleep_time_ms] * len(json_dicts),
        )
        with Pool(n_threads) as p:
            # prepare arguments
            json_files = tqdm.tqdm(
                p.istarmap(
                    write_json_file,
                    args,
                ),
                total=len(json_dicts),
                desc="Saving JSON files",
                unit="file",
            )
            # remove None values
            json_files = [
                json_file for json_file in json_files if json_file is not None
            ]
    else:
        for json_dict in tqdm.tqdm(
            json_dicts,
            desc="Saving JSON files",
            unit="file",
        ):
            dcm_file = json_dict["filepath"]
            dcm_file_basename = os.path.basename(dcm_file)
            json_file = os.path.join(output_dir, dcm_file_basename + ".json")
            write_json_file(json_file, json_dict, sleep_time_ms=sleep_time_ms)
            if os.path.exists(json_file):
                json_files.append(json_file)

    return json_files


def set_n_threads(n_threads: int, logger: logging.Logger = None):
    """Set number of threads to use for parallel processing.

    Args:
        n_threads (int): Number of threads to use for parallel processing.
        logger (logging.Logger): Logger object.
    """
    if logger is None:
        logger = logging.getLogger()
    if n_threads < 1:
        logger.warning(f"Number of threads ({n_threads}) must be greater than 0")
        logger.warning("Setting number of threads to 1")
        n_threads = 1
    elif n_threads > cpu_count():
        logger.warning(
            f"Number of threads ({n_threads}) is greater than the number of CPUs ({cpu_count()})"
        )
        logger.warning("Setting number of threads to the number of CPUs")
        n_threads = cpu_count()
    return n_threads


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


def send_dcm_tags_list_to_elasticsearch(
    dcm_tags_list: list, config: str, logger: logging.Logger = None
):
    """Send list of dictionary representation of the DICOM files to Elasticsearch.

    Args:
        dcm_tags_list (list): List of dictionary representation of the DICOM files.
        config (str): Path to config file in JSON format which defines all variables
                      related to Elasticsearch instance (url, port, index, user, pwd).
        logger (logging.Logger): Logger object.

    Note:
        The dictionary representation of the DICOM files must contain a "filepath" key.
        This key is used to identify the file in Elasticsearch.
    """
    if logger is None:
        logger = create_logger()

    # Load config file
    config = get_config(config)

    # Connect to Elasticsearch instance
    es = Elasticsearch(
        [config["url"]],
        http_auth=(config["user"], config["pwd"]),
        scheme="https",
        port=config["port"],
    )

    # Create index
    if es.indices.exists(config["index"]):
        logger.warning(f"Index {config['index']} already exists")
    else:
        es.indices.create(config["index"])

    # Bulk upload to Elasticsearch
    actions = [
        {
            "_index": config["index"],
            "_type": "_doc",
            "_id": i,
            "_source": dcm_tags,
        }
        for i, dcm_tags in enumerate(dcm_tags_list)
    ]
    helpers.bulk(es, actions)


def process_batches(
    dcm_list_batches: list,
    args: argparse.Namespace,
    logger: logging.Logger = None,
    kwargs: dict = None,
):
    """Process batches of dicom files.

    Args:
        dcm_list_batches (list): List of batches of dicom files to process.
        args (argparse.Namespace): Arguments passed to the main function.
        logger (logging.Logger): Logger object.
        **kwargs: Arbitrary keyword arguments to pass to the `dcmread` function.

    Returns:
        tuple: Tuple containing:
                   * the number of dicom files processed.
                   * the number of dicom files skipped.
                   * the total time spent for extracting tags from dicom files.
                   * the total time spent for saving/uploading tags to JSON/Elasticsearch.
    """
    if logger is None:
        logger = create_logger()

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
                logger=logger,
            )
        else:
            # Upload JSON representation of dicom files in batch to Elasticsearch
            send_dcm_tags_list_to_elasticsearch(
                dcm_tags_list=dcm_tags_list_batch, config=args.config, logger=logger
            )
        toc_save = time.perf_counter()

        # Update counters
        total_time_extraction += toc_extraction - tic_extraction
        total_time_save += toc_save - tic_save
        total_dcm_processed += len(dcm_tags_list_batch)
        total_dcm_skipped += len(dcm_list_batch) - len(dcm_tags_list_batch)

    return total_dcm_processed, total_dcm_skipped, total_time_extraction, total_time_save


def append_profiler_results(
    tsv_file: str,
    n_threads: int,
    batch_size: int,
    process_handler: str,
    max_memory_usage: float,
    total_dcm_processed: int,
    total_dcm_skipped: int,
    total_time: float,
    total_time_extraction: float,
    total_time_save: float,
):
    """Append profiler results to profile file.

    Args:
        tsv_file (str): Path to output TSV file that will contain profiler results.
        n_threads (int): Number of threads used for parallel processing.
        batch_size (int): Batch size for extracting and saving/uploading
                          metadata tags from dicom files.
        process_handler (str): Process handler used for parallel/asynchronous processing.
                               Can be either 'multiprocessing' or 'asyncio'.
        max_memory_usage (float): Maximum memory usage.
        total_dcm_processed (int): Total number of dicom files processed.
        total_dcm_skipped (int): Total number of dicom files skipped.
        total_time (float): Total elapsed time in seconds.
        total_time_extraction (float): Total time spent for extracting tags
                                       from dicom files (seconds).
        total_time_save (float): Total time spent for saving/uploading tags
                                 to JSON/Elasticsearch (seconds).
    """
    if os.path.exists(tsv_file):
        mode = "a"
    else:
        mode = "w"

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

    with open(tsv_file, mode) as f:
        if mode == "w":  # write header at creation
            f.write(
                "\t".join(
                    [
                        "timestamp",
                        "n_threads",
                        "batch_size",
                        "process_handler",
                        "max_memory_usage",
                        "total_dcm_processed",
                        "total_dcm_skipped",
                        "total_time",
                        "total_time_extraction",
                        "total_time_save",
                    ]
                )
                + "\n"
            )
        f.write(
            "\t".join(
                [
                    timestamp,
                    str(n_threads),
                    str(batch_size),
                    process_handler,
                    str(max_memory_usage),
                    str(total_dcm_processed),
                    str(total_dcm_skipped),
                    str(total_time),
                    str(total_time_extraction),
                    str(total_time_save),
                ]
            )
            + "\n"
        )


def main():
    parser = get_parser()
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
    args.n_threads = set_n_threads(args.n_threads, logger=logger)

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
    dcm_list = get_dcm_list(args.input_dcm_list)

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
        (memory_usage, retval) = memory_profiler.memory_usage(
            (process_batches, (dcm_list_batches, args, logger, kwargs)), **profiler_options
        )
        toc = time.perf_counter()

        # Unpack total_dcm_processed and total_dcm_skipped from retval
        total_dcm_processed, total_dcm_skipped, total_time_extraction, total_time_save = retval

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
            total_time_extraction,
            total_time_save,
        )
    else:
        # Process batches of dicom files
        tic = time.perf_counter()
        (total_dcm_processed, total_dcm_skipped, total_time_extraction, total_time_save) = process_batches(
            dcm_list_batches, args, logger, kwargs
        )
        toc = time.perf_counter()
        # Compute total elapsed time
        total_time = toc - tic

    logger.info(f"Run summary:")
    logger.info(f"Number of dicom files processed: {total_dcm_processed}")
    logger.info(f"Number of dicom files skipped: {total_dcm_skipped}")
    logger.info(f"Total time: {total_time:.2f} sec. (Extraction: {total_time_extraction:.2f} sec., Save: {total_time_save:.2f} sec.)")
    logger.info("Finished!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
