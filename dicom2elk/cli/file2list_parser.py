# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module for parsing command line arguments."""


import argparse


def get_parser():
    parser = argparse.ArgumentParser(
        "file2list: A simple and fast package that explore a path and list all file it found in its way ",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        required=True,
        help="The path to start exploring",
    )

    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        required=True,
        help="The max number of file to find",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        required=True,
        help="Specify an output directory to save the list of file. ",
    )

    return parser
