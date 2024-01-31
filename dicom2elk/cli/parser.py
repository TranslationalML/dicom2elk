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

"""Module for parsing command line arguments."""


import argparse

from dicom2elk.info import __copyright__, __packagename__, __version__


def get_file2json_parser():
    parser = argparse.ArgumentParser(
        "dicom2elk: A simple and fast package that extracts relevant tags from dicom files "
        "and uploads them in JSON format to elasticsearch.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-p1",
        "--path",
        type=str,
        required=True,
        help="The path to start exploring.",
    )
    parser.add_argument(
        "-e",
        "--output-err",
        type=str,
        required=True,
        help="Specify an output directory to save the error file. ",
    )
    parser.add_argument(
        "-d ",
        "--output-done",
        type=str,
        required=True,
        help="Specify an output directory to save the parsed file list. ",
    )
    parser.add_argument(
        "-t",
        "--temp-folder",
        type=str,
        required=True,
        help="Specify a temp directory to work. ",
    )
    parser.add_argument(
        "-i",
        "--input-dcm-list",
        type=str,
        required=False,  # not mandatory
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
        "If `--mode json` is specified, all JSON files are also saved in this directory",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="json",
        choices=["json", "elasticsearch"],
        help="Specify the mode to use for saving the extracted metadata tags."
        "Can be either 'json' or 'elasticsearch'",
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


def get_dicom2elk_parser():
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
        "If `--mode json` is specified, all JSON files are also saved in this directory",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="json",
        choices=["json", "elasticsearch"],
        help="Specify the mode to use for saving the extracted metadata tags."
        "Can be either 'json' or 'elasticsearch'",
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


def get_file2list_parser():
    parser = argparse.ArgumentParser(
        "file2list: A simple and fast package that explore a path and list all file it found in its way ",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        required=True,
        help="The path to start exploring.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        required=True,
        help="Specify an output directory to save the list of file.",
    )
    parser.add_argument(
        "-d",
        "--db-file",
        type=str,
        default="file2list.db",
        help="Specify the name of the database file. Default is 'file2list.db'.",
    )
    parser.add_argument(
        "-t",
        "--db-table",
        type=str,
        default="pacs_file_paths",
        help="Specify the name of the table in the database. Default is 'pacs_file_paths'.",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help="The max number of file to find. Default is None.",
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=500,
        help="Batch size for dumping the list of file. Default is 500.",
    )
    parser.add_argument(
        "-s",
        "--sleep-time-ms",
        type=float,
        default=0,
        help="Sleep time in milliseconds to wait between each file processing. "
        "This might be useful to avoid overloading the system.",
    )
    parser.add_argument(
        "-L",
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level. Default is INFO.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"file2list - {__packagename__} {__version__}\n\n{__copyright__}",
    )
    return parser
