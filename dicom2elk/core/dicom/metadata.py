# Copyright 2023-2024 Lausanne University and Lausanne University Hospital, Switzerland & Contributors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module that provides functions to convert DICOM files to JSON files."""

import os
import tqdm
import logging
import time
from multiprocessing import Pool

from pydicom import dcmread

from dicom2elk.utils.io import write_json_file
from dicom2elk.utils.logging import create_logger, get_logger_basefilename
from dicom2elk.core.elasticsearch.api import send_bulk_to_elasticsearch


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
    except Exception as e:
        logger.error(f"Error while processing {dcm_file}: {e}")
        log_file = get_logger_basefilename(logger)
        error_file = log_file.replace('.log', '.errors.txt')
        logger.info(f"Write error in {error_file}")
        with open(error_file, "a") as f:
            f.write(dcm_file)
        return None

    json_dict = dcm_dataset.to_json_dict(suppress_invalid_tags= True)
    json_dict["filepath"] = dcm_file

    if mode == "json":
        try:
            file_name = json_dict["00080018"]["Value"][0]
            json_file = os.path.join(output_dir, file_name + ".json")
            return write_json_file(json_file, json_dict, sleep_time_ms=sleep_time_ms)
        except:
            json_file = os.path.join(output_dir, 'error_'+str(hash(dcm_file)) + ".json")
            return write_json_file(json_file, json_dict, sleep_time_ms=sleep_time_ms)

    time.sleep(sleep_time_ms / 1000.0)  # takes seconds as argument

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
                ).get()
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
