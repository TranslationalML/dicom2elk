# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Tests for dicom2elk.cli.parser module."""

from dicom2elk.cli.parser import get_dicom2elk_parser, get_file2list_parser


def test_get_dicom2elk_parser():
    # Test if get_dicom2elk_parser returns a parser
    assert get_dicom2elk_parser() is not None


def test_get_file2list_parser():
    # Test if get_file2list_parser returns a parser
    assert get_file2list_parser() is not None
