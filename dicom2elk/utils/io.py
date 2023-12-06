# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module that provides functions to read and write all types of files (JSON, DICOM, Text, CSV)."""


import tqdm
from multiprocessing import Pool
from dicom2elk.utils.logging import create_logger


import json
import os
import time
import logging


def read_dcm_list_file(dcm_list_file):
    """Load dicom list file.

    Args:
        dcm_list_file (str): Path to dicom list file.

    Returns:
        list: List of dicom files to process.
    """
    with open(dcm_list_file, "r") as f:
        dcm_list = f.read().splitlines()
    return dcm_list


def write_json_file(
    json_file: str,
    json_dict: dict,
    sleep_time_ms: float = 0,
    logger: logging.Logger = create_logger("INFO"),
):
    """Write JSON file.

    Args:
        json_file (str): Path to JSON file.
        json_dict (dict): Dictionary to save in JSON file.
        sleep_time_ms (float): Sleep time in milliseconds to wait after writing
                               JSON file.
        logger (logging.Logger): Logger instance.

    Returns:
        str: Path of output JSON file.
    """
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
):
    """Write JSON files.

    Args:
        json_dicts (list): List of dictionaries to save in JSON files
                           produced by `get_dcm_tags_list`.
        output_dir (str): Path to output directory.
        n_threads (int): Number of threads to use for parallel processing.

    Note:
        The JSON files are named after the dicom files from which the
        tags were extracted.

    Returns:
        list: List of paths to JSON files.
    """
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
