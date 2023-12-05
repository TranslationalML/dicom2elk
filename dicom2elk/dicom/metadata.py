# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module that provides functions to convert DICOM files to JSON files."""


import os
import nest_asyncio
import tqdm
from tqdm.asyncio import tqdm_asyncio
import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from dicom2elk.io import write_json_file
from dicom2elk.logging import create_logger
from dicom2elk.elasticsearch.api import send_bulk_to_elasticsearch


from pydicom import dcmread


import logging
import time


def get_dcm_tags(
    dcm_file: str,
    sleep_time_ms: str = 0,
    logger: logging.Logger = create_logger("INFO"),
    kwargs: dict = None,
):
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
    logger.debug(f"Processing {dcm_file}")
    stop_before_pixels = kwargs.pop("stop_before_pixels", True)
    try:
        dcm_dataset = dcmread(dcm_file, stop_before_pixels=stop_before_pixels)
        json_dict = dcm_dataset.to_json_dict()
        json_dict["filepath"] = dcm_file
    except Exception as e:
        logger.error(f"Error while processing {dcm_file}: {e}")
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


def extract_metadata_from_dcm(
    dcm_file: str,
    mode: str = "json",
    sleep_time_ms: float = 0.0,
    output_dir: str = None,
    logger: logging.Logger = create_logger("INFO"),
    kwargs: dict = None,
):
    """Extract relevant tags from dicom file.

    Args:
        dcm_file (str): Path to dicom file.
        sleep_time_ms (float): Sleep time in milliseconds to wait after processing
        mode (str): Mode to use for saving the extracted metadata tags.
                    Can be either 'json' or 'elasticsearch'.
        output_dir (str): Path to output directory.
        logger (logging.Logger): Logger object.
        kwargs: Arbitrary keyword arguments to pass to the `dcmread` function.
                In particular, the `stop_before_pixels` argument can be used
                to stop reading file before reading in pixel data when set to True.

    Returns:
        json_dict (dict) or json_file (str): Dictionary representation of the Dataset conforming
                                             to the DICOM JSON Model as described in the
                                             DICOM Standard, Part 18 (if `output_dir` not specified)
                                             or path to JSON file (if `output_dir` specified).

    Raises:
        ValueError: If `mode` is set to 'json' and `output_dir` is not specified.
        ValueError: If `mode` is set to 'elasticsearch' and `config` is not specified.
    """
    if mode == "json" and output_dir is None:
        raise ValueError("If mode is set to 'json', output_dir must be specified.")

    if kwargs is None:
        kwargs = {}

    logger.debug(f"Processing {dcm_file}")

    stop_before_pixels = kwargs.pop("stop_before_pixels", True)
    try:
        dcm_dataset = dcmread(dcm_file, stop_before_pixels=stop_before_pixels)
        json_dict = dcm_dataset.to_json_dict()
        json_dict["filepath"] = dcm_file

        if mode == "json":
            json_file = os.path.join(output_dir, os.path.basename(dcm_file) + ".json")
            return write_json_file(json_file, json_dict, sleep_time_ms=sleep_time_ms)

        time.sleep(sleep_time_ms)

    except Exception as e:
        logging.error(f"Error while processing {dcm_file}: {e}")
        return None

    return json_dict


def extract_metadata_from_dcm_list(
    dcm_list: list,
    output_dir: str = None,
    config: dict = None,
    process_handler: str = "multiprocessing",
    mode: str = "json",
    n_threads: int = 1,
    sleep_time_ms: float = 0,
    logger: logging.Logger = create_logger("INFO"),
    **kwargs,
):
    """Extract list of dictionary representation of the DICOM files conforming to the DICOM JSON Model.

    It uses the `to_json_dict` method of the pydicom package.

    It can be parallelized using the `n_threads` argument which leverages the asyncio package.

    Args:
        dcm_list (list): List of dicom files to process.
        output_dir (str): Path to output directory.
        config (dict): Dictionary containing the Elasticsearch configuration.
        process_handler (str): Process handler to use for parallel/asynchronous processing.
                               Can be either 'multiprocessing' or 'asyncio'.
        mode (str): Mode to use for saving the extracted metadata tags.
                    Can be either 'json' or 'elasticsearch'.
        n_threads (int): Number of threads to use for parallel/asynchronous processing.
                         Defaults to 1.
        sleep_time_ms (float): Sleep time in milliseconds to wait between each file processing.
                               Defaults to 0.
        logger (logging.Logger): Logger object.
        **kwargs: Arbitrary keyword arguments to pass to the `dcmread` function.

    Returns:
        list: List of dictionary representation of the DICOM files conforming to the
              `DICOM JSON Model <http://dicom.nema.org/medical/dicom/current/output/chtml/part18/chapter_F.html>`_.

    Raises:
        ValueError: If `mode` is set to 'json' and `output_dir` is not specified.
        ValueError: If `mode` is set to 'elasticsearch' and `config` is not specified.

    References:
        https://pydicom.github.io/pydicom/dev/reference/generated/pydicom.dataset.Dataset.html#pydicom.dataset.Dataset.to_json_dict
    """
    if mode == "json" and output_dir is None:
        raise ValueError("If mode is set to 'json', output_dir must be specified.")

    if mode == "elasticsearch" and config is None:
        raise ValueError("If mode is set to 'elasticsearch', config must be specified.")

    if n_threads > 1:
        with Pool(n_threads) as p:
            # prepare arguments
            args = zip(
                dcm_list,
                [mode] * len(dcm_list),
                [sleep_time_ms] * len(dcm_list),
                [output_dir] * len(dcm_list),
                [logger] * len(dcm_list),
                [kwargs] * len(dcm_list),
            )
            if process_handler == "multiprocessing":
                processed_dcm_list = p.starmap(
                    extract_metadata_from_dcm,
                    tqdm.tqdm(
                        args,
                        total=len(dcm_list),
                        desc="Extracting and saving tags",
                        unit="file",
                    ),
                )
            elif process_handler == "asyncio":
                processed_dcm_list = p.starmap_async(
                    extract_metadata_from_dcm,
                    tqdm.tqdm(
                        args,
                        total=len(dcm_list),
                        desc="Extracting and saving tags",
                        unit="file",
                    ),
                )
            processed_dcm_list = list(processed_dcm_list)
    else:
        processed_dcm_list = [
            extract_metadata_from_dcm(
                dcm_file,
                mode=mode,
                sleep_time_ms=sleep_time_ms,
                output_dir=output_dir,
                logger=logger,
                kwargs=kwargs,
            )
            for dcm_file in dcm_list
        ]

    if mode == "elasticsearch":
        processed_dcm_list = [
            processed_dcm
            for processed_dcm in processed_dcm_list
            if processed_dcm is not None
        ]
        send_bulk_to_elasticsearch(
            dcm_tags_list=processed_dcm_list,
            config=config,
            logger=logger,
        )
    return processed_dcm_list
